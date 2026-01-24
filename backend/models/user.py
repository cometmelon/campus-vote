"""User model"""
import uuid
from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import Column, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship

from database import Base


class UserRole(str, PyEnum):
    ADMIN = "admin"
    STUDENT = "student"


# Custom GUID type for cross-database UUID support
from sqlalchemy.types import TypeDecorator, CHAR
import uuid as uuid_module

class GUID(TypeDecorator):
    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        return dialect.type_descriptor(CHAR(36))

    def process_bind_param(self, value, dialect):
        if value is not None:
            return str(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            return uuid_module.UUID(value)
        return value


class User(Base):
    __tablename__ = "users"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    student_id = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.STUDENT)
    department_id = Column(GUID(), ForeignKey("departments.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    department = relationship("Department", back_populates="users")
    votes = relationship("Vote", back_populates="user")
    club_memberships = relationship("ClubMember", back_populates="user")
    voting_queue_entries = relationship("VotingQueue", back_populates="user")
