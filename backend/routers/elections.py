"""Elections router"""
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload

from database import get_db
from models import Election, ElectionStatus, Candidate, User
from schemas import (
    ElectionCreate, ElectionWithCandidates, ElectionListItem,
    CandidateCreate, CandidateResponse
)
from routers.auth import get_current_user, get_admin_user

router = APIRouter(prefix="/elections", tags=["Elections"])


@router.get("/", response_model=List[ElectionWithCandidates])
async def get_elections(
    status: Optional[ElectionStatus] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all elections, optionally filtered by status"""
    query = db.query(Election).options(
        joinedload(Election.candidates),
        joinedload(Election.department)
    )
    if status:
        query = query.filter(Election.status == status)
    return query.order_by(Election.created_at.desc()).all()


@router.get("/{election_id}", response_model=ElectionWithCandidates)
async def get_election(
    election_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get election by ID"""
    election = db.query(Election).options(
        joinedload(Election.candidates),
        joinedload(Election.department)
    ).filter(Election.id == election_id).first()
    if not election:
        raise HTTPException(status_code=404, detail="Election not found")
    return election


@router.post("/", response_model=ElectionWithCandidates)
async def create_election(
    election_data: ElectionCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    """Create new election with candidates (Admin only)"""
    election = Election(
        title=election_data.title,
        department_id=election_data.department_id,
        status=election_data.status,
        start_date=election_data.start_date,
        end_date=election_data.end_date,
        batch_size=election_data.batch_size
    )
    db.add(election)
    db.flush()
    
    # Add candidates
    for cand_data in election_data.candidates:
        candidate = Candidate(
            election_id=election.id,
            name=cand_data.name,
            role=cand_data.role,
            photo_url=cand_data.photo_url,
            manifesto=cand_data.manifesto
        )
        db.add(candidate)
    
    db.commit()
    db.refresh(election)
    return election


@router.put("/{election_id}/status")
async def update_election_status(
    election_id: UUID,
    new_status: ElectionStatus = Query(...),
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    """Update election status (Admin only)"""
    election = db.query(Election).filter(Election.id == election_id).first()
    if not election:
        raise HTTPException(status_code=404, detail="Election not found")
    
    election.status = new_status
    db.commit()
    return {"message": f"Election status updated to {new_status.value}"}


@router.delete("/{election_id}")
async def delete_election(
    election_id: UUID,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    """Delete election (Admin only)"""
    election = db.query(Election).filter(Election.id == election_id).first()
    if not election:
        raise HTTPException(status_code=404, detail="Election not found")
    
    db.delete(election)
    db.commit()
    return {"message": "Election deleted"}


# Candidate management within election
@router.post("/{election_id}/candidates", response_model=CandidateResponse)
async def add_candidate(
    election_id: UUID,
    candidate_data: CandidateCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    """Add candidate to election (Admin only)"""
    election = db.query(Election).filter(Election.id == election_id).first()
    if not election:
        raise HTTPException(status_code=404, detail="Election not found")
    
    candidate = Candidate(
        election_id=election_id,
        name=candidate_data.name,
        role=candidate_data.role,
        photo_url=candidate_data.photo_url,
        manifesto=candidate_data.manifesto
    )
    db.add(candidate)
    db.commit()
    db.refresh(candidate)
    return candidate


@router.delete("/{election_id}/candidates/{candidate_id}")
async def remove_candidate(
    election_id: UUID,
    candidate_id: UUID,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    """Remove candidate from election (Admin only)"""
    candidate = db.query(Candidate).filter(
        Candidate.id == candidate_id,
        Candidate.election_id == election_id
    ).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    db.delete(candidate)
    db.commit()
    return {"message": "Candidate removed"}
