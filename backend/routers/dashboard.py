"""Dashboard router"""
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, select

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
    # Optimized query to fetch all counts in one round-trip
    stmt = select(
        select(func.count(User.id)).filter(User.role == UserRole.STUDENT).scalar_subquery(),
        select(func.count(Election.id)).filter(Election.status == ElectionStatus.ACTIVE).scalar_subquery(),
        select(func.count(Club.id)).scalar_subquery()
    )
    result = db.execute(stmt).one()
    total_students, active_elections, registered_clubs = result
    
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
    
    for dept in departments:
        dept_students = db.query(User).filter(
            User.department_id == dept.id,
            User.role == UserRole.STUDENT
        ).count()
        
        dept_votes = db.query(Vote).join(User).filter(
            User.department_id == dept.id
        ).count()
        
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
