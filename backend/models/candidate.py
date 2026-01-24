"""Candidate model"""
import uuid
from sqlalchemy import Column, String, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship

from database import Base
from models.user import GUID


class Candidate(Base):
    __tablename__ = "candidates"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    election_id = Column(GUID(), ForeignKey("elections.id"), nullable=False)
    name = Column(String(255), nullable=False)
    role = Column(String(100), nullable=False)  # e.g., "President", "Secretary"
    photo_url = Column(String(500), nullable=True)
    manifesto = Column(Text, nullable=True)
    vote_count = Column(Integer, default=0)
    
    # Relationships
    election = relationship("Election", back_populates="candidates")
    votes = relationship("Vote", back_populates="candidate")
