"""Vote model"""
import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from database import Base
from models.user import GUID


class Vote(Base):
    __tablename__ = "votes"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    election_id = Column(GUID(), ForeignKey("elections.id"), nullable=False)
    user_id = Column(GUID(), ForeignKey("users.id"), nullable=False)
    candidate_id = Column(GUID(), ForeignKey("candidates.id"), nullable=False)
    voted_at = Column(DateTime, default=datetime.utcnow)
    
    # Ensure one vote per user per election
    __table_args__ = (
        UniqueConstraint('election_id', 'user_id', name='uq_election_user_vote'),
    )
    
    # Relationships
    election = relationship("Election", back_populates="votes")
    user = relationship("User", back_populates="votes")
    candidate = relationship("Candidate", back_populates="votes")
