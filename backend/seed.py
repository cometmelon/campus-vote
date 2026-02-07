"""Seed demo data for development"""
import os
import secrets
import string
from datetime import datetime, timedelta
import logging
import secrets
import string

from config import settings
from database import SessionLocal
from models import User, UserRole, Department, Election, ElectionStatus, Candidate, Club, ClubMember, MemberRole
from routers.auth import get_password_hash

logger = logging.getLogger(__name__)


def seed_demo_data():
    """Seed the database with demo data"""
    db = SessionLocal()
    
    try:
        # Check if already seeded
        if db.query(User).filter(User.student_id == settings.ADMIN_STUDENT_ID).first():
            logger.info("Database already seeded, skipping...")
            return
        
        logger.info("Seeding demo data...")
        
        # Create departments
        departments = [
            Department(code="CSE", name="Computer Science & Engineering", total_students=450),
            Department(code="ECE", name="Electronics & Communication Engineering", total_students=400),
            Department(code="MECH", name="Mechanical Engineering", total_students=350),
            Department(code="CIVIL", name="Civil Engineering", total_students=300),
            Department(code="ARTS", name="Arts & Humanities", total_students=200),
            Department(code="SCI", name="Basic Sciences", total_students=150),
        ]
        for dept in departments:
            db.add(dept)
        db.flush()
        
        cse_dept = departments[0]
        ece_dept = departments[1]
        
        # Determine admin password
        admin_password = settings.ADMIN_PASSWORD
        if not admin_password:
            # Generate a secure random password if not provided
            alphabet = string.ascii_letters + string.digits
            admin_password = ''.join(secrets.choice(alphabet) for i in range(16))
            print("\n=========================================================")
            print("⚠️  ADMIN_PASSWORD not set. Generated random password:")
            print(f"👉  {admin_password}")
            print("=========================================================\n")
            logger.warning("Generated random admin password")
        else:
            logger.info("Using configured ADMIN_PASSWORD.")

        # Create admin user
        admin = User(
            student_id=settings.ADMIN_STUDENT_ID,
            email=settings.ADMIN_EMAIL,
            password_hash=get_password_hash(admin_password),
            name="Admin User",
            role=UserRole.ADMIN
        )
        db.add(admin)
        
        # Create demo students
        students = [
            User(
                student_id="student",
                email="student@campusvote.edu",
                password_hash=get_password_hash("student"),
                name="Demo Student",
                role=UserRole.STUDENT,
                department_id=cse_dept.id
            ),
            User(
                student_id="CSE001",
                email="cse001@campusvote.edu",
                password_hash=get_password_hash("password123"),
                name="Alice Johnson",
                role=UserRole.STUDENT,
                department_id=cse_dept.id
            ),
            User(
                student_id="ECE001",
                email="ece001@campusvote.edu",
                password_hash=get_password_hash("password123"),
                name="Bob Smith",
                role=UserRole.STUDENT,
                department_id=ece_dept.id
            ),
        ]
        for student in students:
            db.add(student)
        db.flush()
        
        # Create elections
        now = datetime.utcnow()
        
        elections = [
            Election(
                title="Student Council President",
                department_id=None,  # All departments - ACTIVE
                status=ElectionStatus.ACTIVE,
                start_date=now - timedelta(days=1),
                end_date=now + timedelta(days=7),
                batch_size=60
            ),
            Election(
                title="CSE Office Bearer 2026",
                department_id=cse_dept.id,
                status=ElectionStatus.ACTIVE,
                start_date=now - timedelta(days=1),
                end_date=now + timedelta(days=5),
                batch_size=60
            ),
            Election(
                title="ECE Department Election 2026",
                department_id=ece_dept.id,
                status=ElectionStatus.ACTIVE,
                start_date=now,
                end_date=now + timedelta(days=1),
                batch_size=60
            ),
            Election(
                title="CSE Department Representative",
                department_id=cse_dept.id,
                status=ElectionStatus.FINISHED,
                start_date=now - timedelta(days=8),
                end_date=now - timedelta(days=1),
                batch_size=60
            ),
        ]
        for election in elections:
            db.add(election)
        db.flush()
        
        # Add candidates
        candidates = [
            # Student Council President
            Candidate(
                election_id=elections[0].id,
                name="Michael Chen",
                role="President",
                photo_url="https://i.pravatar.cc/150?u=michael",
                manifesto="A campus for everyone. Better facilities, more events.",
                vote_count=0
            ),
            Candidate(
                election_id=elections[0].id,
                name="Sarah Williams",
                role="President",
                photo_url="https://i.pravatar.cc/150?u=sarah",
                manifesto="Innovation and inclusion. Let's build the future together.",
                vote_count=0
            ),
            # CSE Office Bearer
            Candidate(
                election_id=elections[1].id,
                name="Priya Sharma",
                role="Secretary",
                photo_url="https://i.pravatar.cc/150?u=priya",
                manifesto="Better labs, more hackathons, industry connections.",
                vote_count=0
            ),
            Candidate(
                election_id=elections[1].id,
                name="Raj Patel",
                role="Secretary",
                photo_url="https://i.pravatar.cc/150?u=raj",
                manifesto="Student welfare first. More coding competitions.",
                vote_count=0
            ),
            # ECE Department Election
            Candidate(
                election_id=elections[2].id,
                name="Surya S",
                role="President",
                photo_url="https://i.pravatar.cc/150?u=surya",
                manifesto="No manifesto provided.",
                vote_count=0
            ),
        ]
        for candidate in candidates:
            db.add(candidate)
        
        # Create clubs
        space_club = Club(
            name="Space club",
            category="tech club",
            description="aim beyond space",
            status="active"
        )
        db.add(space_club)
        db.flush()
        
        # Add member to club
        club_member = ClubMember(
            club_id=space_club.id,
            user_id=students[0].id,
            role=MemberRole.MEMBER
        )
        db.add(club_member)
        
        db.commit()
        logger.info("Demo data seeded successfully!")
        
    except Exception as e:
        logger.error(f"Error seeding data: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    from database import Base, engine
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    seed_demo_data()
