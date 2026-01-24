"""Voting Queue model for batch-based voting"""
import uuid
from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import Column, String, DateTime, ForeignKey, Enum, Integer
from sqlalchemy.orm import relationship

from database import Base
from models.user import GUID


class QueueStatus(str, PyEnum):
    PENDING = "pending"
    NOTIFIED = "notified"
    VOTED = "voted"
    EXPIRED = "expired"


class VotingQueue(Base):
    __tablename__ = "voting_queue"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    election_id = Column(GUID(), ForeignKey("elections.id"), nullable=False)
    user_id = Column(GUID(), ForeignKey("users.id"), nullable=False)
    status = Column(Enum(QueueStatus), default=QueueStatus.PENDING)
    voting_token = Column(String(255), unique=True, nullable=False)
    batch_number = Column(Integer, default=1)
    notified_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    election = relationship("Election", back_populates="voting_queue")
    user = relationship("User", back_populates="voting_queue_entries")
