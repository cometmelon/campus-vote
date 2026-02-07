import sys
import os
import unittest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Add backend directory to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from main import app
from database import Base, get_db
from models import User, UserRole, Election, ElectionStatus, Department, Vote, Candidate
from routers.auth import get_admin_user

class TestDashboardStats(unittest.TestCase):

    def setUp(self):
        # Setup in-memory DB
        self.engine = create_engine(
            "sqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool
        )
        Base.metadata.create_all(self.engine)
        print(f"Tables created: {Base.metadata.tables.keys()}")
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.db = self.SessionLocal()

        # Override get_db dependency
        def override_get_db():
            try:
                yield self.db
            finally:
                pass

        # Override get_admin_user dependency
        def override_get_admin_user():
             # Return a fake admin user
             u = User(id="admin_id", role=UserRole.ADMIN, name="Admin", email="admin@test.com", password_hash="hash", student_id="admin")
             return u

        app.dependency_overrides[get_db] = override_get_db
        app.dependency_overrides[get_admin_user] = override_get_admin_user
        self.client = TestClient(app)

    def tearDown(self):
        self.db.close()
        Base.metadata.drop_all(self.engine)

    def test_get_dashboard_stats_correct_eligibility(self):
        # 1. Create Departments
        dept_cs = Department(code="CS", name="Computer Science", total_students=10)
        dept_math = Department(code="MATH", name="Mathematics", total_students=5)
        self.db.add(dept_cs)
        self.db.add(dept_math)
        self.db.commit()

        # 2. Create Students
        # 10 CS students
        for i in range(10):
            self.db.add(User(
                student_id=f"cs{i}",
                email=f"cs{i}@test.com",
                password_hash="hash",
                name=f"CS Student {i}",
                role=UserRole.STUDENT,
                department_id=dept_cs.id
            ))

        # 5 Math students
        for i in range(5):
            self.db.add(User(
                student_id=f"math{i}",
                email=f"math{i}@test.com",
                password_hash="hash",
                name=f"Math Student {i}",
                role=UserRole.STUDENT,
                department_id=dept_math.id
            ))

        # 1 General student (no dept)
        gen_student = User(
            student_id="gen1",
            email="gen1@test.com",
            password_hash="hash",
            name="General Student 1",
            role=UserRole.STUDENT,
            department_id=None
        )
        self.db.add(gen_student)
        self.db.commit()

        # Total students: 16

        # 3. Create Elections
        # Election 1: General (All students eligible)
        e1 = Election(
            title="General Election",
            status=ElectionStatus.ACTIVE,
            start_date=datetime.utcnow(),
            end_date=datetime.utcnow() + timedelta(days=1),
            department_id=None
        )
        # Election 2: CS Dept (Only CS students eligible)
        e2 = Election(
            title="CS Election",
            status=ElectionStatus.ACTIVE,
            start_date=datetime.utcnow(),
            end_date=datetime.utcnow() + timedelta(days=1),
            department_id=dept_cs.id
        )
        self.db.add(e1)
        self.db.add(e2)
        self.db.commit()

        # 4. Create 1 Vote for General Election
        cand1 = Candidate(
            election_id=e1.id,
            name="Candidate 1",
            role="President"
        )
        self.db.add(cand1)
        self.db.commit()

        v1 = Vote(
            election_id=e1.id,
            user_id=gen_student.id,
            candidate_id=cand1.id,
            voted_at=datetime.utcnow()
        )
        self.db.add(v1)
        self.db.commit()

        # Expected Logic:
        # Total Votes = 1
        # Eligible for E1 = 16
        # Eligible for E2 = 10
        # Total Eligible = 26
        # Turnout = (1 / 26) * 100 = 3.846... -> round(3.8)

        # Buggy Logic:
        # Total Eligible = 16 * 2 = 32
        # Turnout = (1 / 32) * 100 = 3.125 -> round(3.1)

        response = self.client.get("/dashboard/stats")
        self.assertEqual(response.status_code, 200)
        data = response.json()

        print(f"Stats Response: {data}")

        # Check if turnout is closer to 3.8 or 3.1
        turnout = data['voter_turnout']

        # 3.8 is expected if fixed. 3.1 if buggy.
        self.assertAlmostEqual(turnout, 3.8, delta=0.1, msg=f"Turnout {turnout} does not match expected 3.8")

if __name__ == '__main__':
    unittest.main()
