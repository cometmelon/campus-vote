"""Dashboard router"""
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from database import get_db
from models import User, UserRole, Election, ElectionStatus, Club, Vote, Department
from schemas import DashboardStats, DepartmentTurnout, RecentElection
from routers.auth import get_admin_user

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    """Get dashboard KPI stats (Admin only)"""
    total_students = db.query(User).filter(User.role == UserRole.STUDENT).count()
    active_elections = db.query(Election).filter(
        Election.status == ElectionStatus.ACTIVE
    ).count()
    registered_clubs = db.query(Club).count()
    
    # Calculate overall voter turnout
    total_votes = db.query(Vote).count()
    total_eligible = total_students * db.query(Election).filter(
        Election.status.in_([ElectionStatus.ACTIVE, ElectionStatus.FINISHED])
    ).count()
    voter_turnout = (total_votes / total_eligible * 100) if total_eligible > 0 else 0
    
    return DashboardStats(
        total_students=total_students,
        active_elections=active_elections,
        voter_turnout=round(voter_turnout, 1),
        registered_clubs=registered_clubs
    )


@router.get("/turnout", response_model=List[DepartmentTurnout])
async def get_department_turnout(
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    """Get voter turnout by department (Admin only)"""
    departments = db.query(Department).all()
    result = []
    
    # Batch query for student counts
    student_counts_query = db.query(
        User.department_id,
        func.count(User.id)
    ).filter(
        User.role == UserRole.STUDENT
    ).group_by(User.department_id).all()

    # Convert to dict for O(1) lookup
    student_counts = {dept_id: count for dept_id, count in student_counts_query}

    # Batch query for vote counts
    vote_counts_query = db.query(
        User.department_id,
        func.count(Vote.id)
    ).select_from(Vote).join(User).group_by(User.department_id).all()

    # Convert to dict
    vote_counts = {dept_id: count for dept_id, count in vote_counts_query}

    for dept in departments:
        dept_students = student_counts.get(dept.id, 0)
        dept_votes = vote_counts.get(dept.id, 0)
        
        turnout = (dept_votes / dept_students * 100) if dept_students > 0 else 0
        result.append(DepartmentTurnout(
            department=dept.code,
            turnout=round(turnout, 1)
        ))
    
    return result


@router.get("/recent-elections", response_model=List[RecentElection])
async def get_recent_elections(
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    """Get recent elections (Admin only)"""
    elections = db.query(Election).order_by(
        Election.created_at.desc()
    ).limit(5).all()
    
    return [
        RecentElection(
            id=e.id,
            title=e.title,
            start_date=e.start_date,
            end_date=e.end_date,
            status=e.status
        )
        for e in elections
    ]
