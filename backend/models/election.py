"""Election model"""
import uuid
from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import Column, String, DateTime, ForeignKey, Enum, Integer
from sqlalchemy.orm import relationship

from database import Base
from models.user import GUID


class ElectionStatus(str, PyEnum):
    PLANNED = "planned"
    ACTIVE = "active"
    FINISHED = "finished"


class Election(Base):
    __tablename__ = "elections"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    department_id = Column(GUID(), ForeignKey("departments.id"), nullable=True)  # null = all departments
    status = Column(Enum(ElectionStatus), default=ElectionStatus.PLANNED)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    batch_size = Column(Integer, default=60)  # For load balancing
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    department = relationship("Department", back_populates="elections")
    candidates = relationship("Candidate", back_populates="election", cascade="all, delete-orphan")
    votes = relationship("Vote", back_populates="election")
    voting_queue = relationship("VotingQueue", back_populates="election")
