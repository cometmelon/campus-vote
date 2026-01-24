"""Department model"""
import uuid
from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship

from database import Base
from models.user import GUID


class Department(Base):
    __tablename__ = "departments"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    code = Column(String(20), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    total_students = Column(Integer, default=0)
    
    # Relationships
    users = relationship("User", back_populates="department")
    elections = relationship("Election", back_populates="department")
