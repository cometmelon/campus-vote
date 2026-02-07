"""Queue service for batch processing"""
import secrets
from datetime import datetime, timedelta
from typing import List, Tuple
import math

from sqlalchemy.orm import Session

from config import settings
from models import Election, User, VotingQueue, QueueStatus


def create_voting_queue_entries(
    db: Session,
    election: Election,
    students: List[User],
    batch_size: int
) -> Tuple[int, int]:
    """
    Create voting queue entries for students with batch assignment.
    Returns (total_batches, first_batch_count)
    """
    if batch_size <= 0:
        return 0, 0

    total_students = len(students)
    total_batches = math.ceil(total_students / batch_size)
    expires_at = datetime.utcnow() + timedelta(hours=settings.VOTING_LINK_EXPIRE_HOURS)
    
    first_batch_count = 0
    
    # Get all student IDs to filter the bulk query
    student_ids = [student.id for student in students]

    # Fetch existing entries in bulk to avoid N+1 queries
    existing_user_ids = set(
        user_id for (user_id,) in db.query(VotingQueue.user_id).filter(
            VotingQueue.election_id == election.id,
            VotingQueue.user_id.in_(student_ids)
        ).all()
    )

    for i, student in enumerate(students):
        if student.id in existing_user_ids:
            continue

        batch_number = (i // batch_size) + 1
        
        entry = VotingQueue(
            election_id=election.id,
            user_id=student.id,
            voting_token=secrets.token_urlsafe(32),
            batch_number=batch_number,
            status=QueueStatus.PENDING,
            expires_at=expires_at
        )
        db.add(entry)
        
        if batch_number == 1:
            first_batch_count += 1
    
    db.commit()
    return total_batches, first_batch_count


def process_next_batch(db: Session, election_id) -> int:
    """
    Process the next pending batch for an election.
    Returns number of entries processed.
    """
    from services.email_service import send_voting_emails
    from models import Election
    
    # Find next batch number with pending entries
    pending = db.query(VotingQueue).filter(
        VotingQueue.election_id == election_id,
        VotingQueue.status == QueueStatus.PENDING
    ).order_by(VotingQueue.batch_number).first()
    
    if not pending:
        return 0
    
    next_batch = pending.batch_number
    
    # Get all entries for this batch
    batch_entries = db.query(VotingQueue).filter(
        VotingQueue.election_id == election_id,
        VotingQueue.batch_number == next_batch,
        VotingQueue.status == QueueStatus.PENDING
    ).all()
    
    election = db.query(Election).filter(Election.id == election_id).first()
    
    return send_voting_emails(db, batch_entries, election)
