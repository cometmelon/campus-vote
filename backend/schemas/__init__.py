from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, EmailStr

from models.user import UserRole


# Auth schemas
class UserLogin(BaseModel):
    student_id: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: Optional[UUID] = None


# User schemas
class UserBase(BaseModel):
    student_id: str
    email: EmailStr
    name: str
    role: UserRole = UserRole.STUDENT
    department_id: Optional[UUID] = None


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


class UserWithDepartment(UserResponse):
    department: Optional["DepartmentResponse"] = None


# Department schemas
class DepartmentBase(BaseModel):
    code: str
    name: str
    total_students: int = 0


class DepartmentCreate(DepartmentBase):
    pass


class DepartmentResponse(DepartmentBase):
    id: UUID

    class Config:
        from_attributes = True


# Election schemas
from models.election import ElectionStatus


class CandidateBase(BaseModel):
    name: str
    role: str
    photo_url: Optional[str] = None
    manifesto: Optional[str] = None


class CandidateCreate(CandidateBase):
    pass


class CandidateResponse(CandidateBase):
    id: UUID
    election_id: UUID
    vote_count: int = 0

    class Config:
        from_attributes = True


class ElectionBase(BaseModel):
    title: str
    department_id: Optional[UUID] = None
    status: ElectionStatus = ElectionStatus.PLANNED
    start_date: datetime
    end_date: datetime
    batch_size: int = 60


class ElectionCreate(ElectionBase):
    candidates: List[CandidateCreate] = []


class ElectionResponse(ElectionBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


class ElectionWithCandidates(ElectionResponse):
    candidates: List[CandidateResponse] = []
    department: Optional[DepartmentResponse] = None


class ElectionListItem(BaseModel):
    id: UUID
    title: str
    department: Optional[DepartmentResponse] = None
    status: ElectionStatus
    start_date: datetime
    end_date: datetime

    class Config:
        from_attributes = True


# Vote schemas
class VoteCreate(BaseModel):
    election_id: UUID
    candidate_id: UUID


class VoteResponse(BaseModel):
    id: UUID
    election_id: UUID
    user_id: UUID
    candidate_id: UUID
    voted_at: datetime

    class Config:
        from_attributes = True


# Voting Queue schemas
from models.voting_queue import QueueStatus


class VotingQueueCreate(BaseModel):
    election_id: UUID
    batch_size: int = 60


class VotingQueueResponse(BaseModel):
    id: UUID
    election_id: UUID
    user_id: UUID
    status: QueueStatus
    voting_token: str
    batch_number: int
    notified_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class SendVotingLinksRequest(BaseModel):
    election_id: UUID
    department_id: Optional[UUID] = None
    batch_size: int = 60


class SendVotingLinksResponse(BaseModel):
    total_students: int
    batches: int
    first_batch_sent: int
    message: str


class TokenValidationResponse(BaseModel):
    election: ElectionWithCandidates
    valid: bool


# Club schemas
from models.club import ClubStatus, MemberRole


class ClubBase(BaseModel):
    name: str
    category: Optional[str] = None
    description: Optional[str] = None
    status: ClubStatus = ClubStatus.ACTIVE


class ClubCreate(ClubBase):
    pass


class ClubMemberResponse(BaseModel):
    id: UUID
    user_id: UUID
    role: MemberRole
    joined_at: datetime
    user: Optional[UserResponse] = None

    class Config:
        from_attributes = True


class ClubResponse(ClubBase):
    id: UUID
    member_count: int = 0

    class Config:
        from_attributes = True


class ClubWithMembers(ClubResponse):
    members: List[ClubMemberResponse] = []


# Dashboard schemas
class DashboardStats(BaseModel):
    total_students: int
    active_elections: int
    voter_turnout: float
    registered_clubs: int


class DepartmentTurnout(BaseModel):
    department: str
    turnout: float


class RecentElection(BaseModel):
    id: UUID
    title: str
    start_date: datetime
    end_date: datetime
    status: ElectionStatus


# Forward references
UserWithDepartment.model_rebuild()
