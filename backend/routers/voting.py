"""Voting router with queue management"""
import secrets
from datetime import datetime, timedelta
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session, joinedload

from config import settings
from database import get_db
from models import (
    Election, ElectionStatus, User, UserRole, Vote, Candidate,
    VotingQueue, QueueStatus
)
from schemas import (
    VoteCreate, VoteResponse, SendVotingLinksRequest, 
    SendVotingLinksResponse, ElectionWithCandidates,
    VotingValidateResponse
)
from routers.auth import get_current_user, get_admin_user
from services.email_service import send_voting_emails, send_voting_emails_bg
from services.queue_service import create_voting_queue_entries

router = APIRouter(prefix="/voting", tags=["Voting"])


@router.post("/send-links", response_model=SendVotingLinksResponse)
async def send_voting_links(
    request: SendVotingLinksRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    """Send voting links to students (Admin only)"""
    election = db.query(Election).filter(Election.id == request.election_id).first()
    if not election:
        raise HTTPException(status_code=404, detail="Election not found")
    if election.status != ElectionStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="Election is not active")
    
    # Get eligible students
    query = db.query(User).filter(User.role == UserRole.STUDENT)
    if election.department_id:
        query = query.filter(User.department_id == election.department_id)
    elif request.department_id:
        query = query.filter(User.department_id == request.department_id)
    
    students = query.all()
    if not students:
        raise HTTPException(status_code=400, detail="No eligible students found")
    
    # Create queue entries and send first batch
    batch_size = request.batch_size or settings.DEFAULT_BATCH_SIZE
    total_batches, first_batch_count = create_voting_queue_entries(
        db, election, students, batch_size
    )
    
    # Send emails for first batch
    first_batch = db.query(VotingQueue).options(
        joinedload(VotingQueue.user)
    ).filter(
        VotingQueue.election_id == election.id,
        VotingQueue.batch_number == 1
    ).all()
    
    background_tasks.add_task(send_voting_emails_bg, [e.id for e in first_batch], election.id)
    
    return SendVotingLinksResponse(
        total_students=len(students),
        batches=total_batches,
        first_batch_sent=first_batch_count,
        message=f"Voting links queued. First batch of {first_batch_count} emails sent."
    )


@router.get("/validate/{token}", response_model=VotingValidateResponse)
async def validate_voting_token(token: str, db: Session = Depends(get_db)):
    """Validate a voting token and return election info"""
    queue_entry = db.query(VotingQueue).filter(
        VotingQueue.voting_token == token
    ).first()
    
    if not queue_entry:
        raise HTTPException(status_code=404, detail="Invalid voting token")
    
    if queue_entry.status == QueueStatus.VOTED:
        raise HTTPException(status_code=400, detail="Vote already cast")
    
    if queue_entry.status == QueueStatus.EXPIRED or (
        queue_entry.expires_at and queue_entry.expires_at < datetime.utcnow()
    ):
        queue_entry.status = QueueStatus.EXPIRED
        db.commit()
        raise HTTPException(status_code=400, detail="Voting token expired")
    
    election = db.query(Election).options(
        joinedload(Election.candidates)
    ).filter(Election.id == queue_entry.election_id).first()
    
    return {
        "election": election,
        "valid": True
    }


@router.post("/cast/{token}", response_model=VoteResponse)
async def cast_vote(
    token: str,
    vote_data: VoteCreate,
    db: Session = Depends(get_db)
):
    """Cast a vote using voting token"""
    queue_entry = db.query(VotingQueue).filter(
        VotingQueue.voting_token == token
    ).first()
    
    if not queue_entry:
        raise HTTPException(status_code=404, detail="Invalid voting token")
    
    if queue_entry.status == QueueStatus.VOTED:
        raise HTTPException(status_code=400, detail="Vote already cast")
    
    if queue_entry.expires_at and queue_entry.expires_at < datetime.utcnow():
        queue_entry.status = QueueStatus.EXPIRED
        db.commit()
        raise HTTPException(status_code=400, detail="Voting token expired")
    
    # Verify election matches
    if queue_entry.election_id != vote_data.election_id:
        raise HTTPException(status_code=400, detail="Election mismatch")
    
    # Verify candidate belongs to election
    candidate = db.query(Candidate).filter(
        Candidate.id == vote_data.candidate_id,
        Candidate.election_id == vote_data.election_id
    ).first()
    if not candidate:
        raise HTTPException(status_code=400, detail="Invalid candidate")
    
    # Check for existing vote
    existing_vote = db.query(Vote).filter(
        Vote.election_id == vote_data.election_id,
        Vote.user_id == queue_entry.user_id
    ).first()
    if existing_vote:
        raise HTTPException(status_code=400, detail="Already voted in this election")
    
    # Cast vote
    vote = Vote(
        election_id=vote_data.election_id,
        user_id=queue_entry.user_id,
        candidate_id=vote_data.candidate_id
    )
    db.add(vote)
    
    # Update candidate vote count
    candidate.vote_count = Candidate.vote_count + 1
    
    # Update queue status
    queue_entry.status = QueueStatus.VOTED
    
    db.commit()
    db.refresh(vote)
    return vote


@router.get("/active", response_model=List[ElectionWithCandidates])
async def get_active_elections_for_student(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get active elections for current student based on department"""
    query = db.query(Election).options(
        joinedload(Election.candidates),
        joinedload(Election.department)
    ).filter(Election.status == ElectionStatus.ACTIVE)
    
    # Filter by department for students
    if current_user.role == UserRole.STUDENT and current_user.department_id:
        from sqlalchemy import or_
        query = query.filter(
            or_(
                Election.department_id == None,  # All-department elections
                Election.department_id == current_user.department_id
            )
        )
    
    return query.all()


@router.get("/queue-status/{election_id}")
async def get_queue_status(
    election_id: UUID,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    """Get voting queue status for an election (Admin only)"""
    total = db.query(VotingQueue).filter(
        VotingQueue.election_id == election_id
    ).count()
    
    pending = db.query(VotingQueue).filter(
        VotingQueue.election_id == election_id,
        VotingQueue.status == QueueStatus.PENDING
    ).count()
    
    notified = db.query(VotingQueue).filter(
        VotingQueue.election_id == election_id,
        VotingQueue.status == QueueStatus.NOTIFIED
    ).count()
    
    voted = db.query(VotingQueue).filter(
        VotingQueue.election_id == election_id,
        VotingQueue.status == QueueStatus.VOTED
    ).count()
    
    return {
        "total": total,
        "pending": pending,
        "notified": notified,
        "voted": voted,
        "participation_rate": (voted / total * 100) if total > 0 else 0
    }
