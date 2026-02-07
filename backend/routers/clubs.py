"""Clubs router"""
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from database import get_db
from models import Club, ClubMember, User, MemberRole
from schemas import ClubCreate, ClubResponse, ClubWithMembers, ClubMemberResponse
from routers.auth import get_current_user, get_admin_user

router = APIRouter(prefix="/clubs", tags=["Clubs"])


@router.get("/", response_model=List[ClubResponse])
async def get_clubs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all clubs"""
    clubs_with_counts = (
        db.query(Club, func.count(ClubMember.id).label("member_count"))
        .outerjoin(Club.members)
        .group_by(Club.id)
        .all()
    )
    return [
        ClubResponse(
            id=club.id,
            name=club.name,
            category=club.category,
            description=club.description,
            status=club.status,
            member_count=count
        )
        for club, count in clubs_with_counts
    ]


@router.get("/{club_id}", response_model=ClubWithMembers)
async def get_club(
    club_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get club by ID with members"""
    club = db.query(Club).options(
        joinedload(Club.members).joinedload(ClubMember.user)
    ).filter(Club.id == club_id).first()
    
    if not club:
        raise HTTPException(status_code=404, detail="Club not found")
    
    return ClubWithMembers(
        id=club.id,
        name=club.name,
        category=club.category,
        description=club.description,
        status=club.status,
        member_count=club.member_count,
        members=[
            ClubMemberResponse(
                id=m.id,
                user_id=m.user_id,
                role=m.role,
                joined_at=m.joined_at,
                user=m.user
            )
            for m in club.members
        ]
    )


@router.post("/", response_model=ClubResponse)
async def create_club(
    club_data: ClubCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    """Create new club (Admin only)"""
    existing = db.query(Club).filter(Club.name == club_data.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Club name already exists")
    
    club = Club(
        name=club_data.name,
        category=club_data.category,
        description=club_data.description,
        status=club_data.status
    )
    db.add(club)
    db.commit()
    db.refresh(club)
    
    return ClubResponse(
        id=club.id,
        name=club.name,
        category=club.category,
        description=club.description,
        status=club.status,
        member_count=0
    )


@router.delete("/{club_id}")
async def delete_club(
    club_id: UUID,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    """Delete club (Admin only)"""
    club = db.query(Club).filter(Club.id == club_id).first()
    if not club:
        raise HTTPException(status_code=404, detail="Club not found")
    
    db.delete(club)
    db.commit()
    return {"message": "Club deleted"}


@router.post("/{club_id}/members/{user_id}")
async def add_member(
    club_id: UUID,
    user_id: UUID,
    role: MemberRole = MemberRole.MEMBER,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    """Add member to club (Admin only)"""
    club = db.query(Club).filter(Club.id == club_id).first()
    if not club:
        raise HTTPException(status_code=404, detail="Club not found")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    existing = db.query(ClubMember).filter(
        ClubMember.club_id == club_id,
        ClubMember.user_id == user_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="User already a member")
    
    member = ClubMember(club_id=club_id, user_id=user_id, role=role)
    db.add(member)
    db.commit()
    return {"message": "Member added"}


@router.delete("/{club_id}/members/{user_id}")
async def remove_member(
    club_id: UUID,
    user_id: UUID,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    """Remove member from club (Admin only)"""
    member = db.query(ClubMember).filter(
        ClubMember.club_id == club_id,
        ClubMember.user_id == user_id
    ).first()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    
    db.delete(member)
    db.commit()
    return {"message": "Member removed"}
