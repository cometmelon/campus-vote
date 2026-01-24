"""Club models"""
import uuid
from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import Column, String, DateTime, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship

from database import Base
from models.user import GUID


class ClubStatus(str, PyEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class MemberRole(str, PyEnum):
    PRESIDENT = "president"
    VICE_PRESIDENT = "vice_president"
    SECRETARY = "secretary"
    TREASURER = "treasurer"
    MEMBER = "member"


class Club(Base):
    __tablename__ = "clubs"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, unique=True)
    category = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    status = Column(Enum(ClubStatus), default=ClubStatus.ACTIVE)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    members = relationship("ClubMember", back_populates="club", cascade="all, delete-orphan")
    
    @property
    def member_count(self):
        return len(self.members)


class ClubMember(Base):
    __tablename__ = "club_members"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    club_id = Column(GUID(), ForeignKey("clubs.id"), nullable=False)
    user_id = Column(GUID(), ForeignKey("users.id"), nullable=False)
    role = Column(Enum(MemberRole), default=MemberRole.MEMBER)
    joined_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    club = relationship("Club", back_populates="members")
    user = relationship("User", back_populates="club_memberships")
