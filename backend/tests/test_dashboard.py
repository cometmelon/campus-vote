from routers.auth import get_admin_user
from models import User, UserRole, Department, Election, ElectionStatus, Vote, Candidate
from datetime import datetime, timedelta

def test_voter_turnout_calculation_bug(client, db_session):
    # Override admin auth
    from main import app
    def override_get_admin_user():
        return User(id="admin_id", role=UserRole.ADMIN, name="Admin")

    app.dependency_overrides[get_admin_user] = override_get_admin_user

    # Create Departments
    dept_a = Department(code="A", name="Department A", total_students=100)
    dept_b = Department(code="B", name="Department B", total_students=100)
    db_session.add_all([dept_a, dept_b])
    db_session.commit()

    # Create Students
    # 2 students in Dept A, 1 in Dept B
    s1 = User(student_id="S1", email="s1@test.com", password_hash="hash", name="S1", role=UserRole.STUDENT, department_id=dept_a.id)
    s2 = User(student_id="S2", email="s2@test.com", password_hash="hash", name="S2", role=UserRole.STUDENT, department_id=dept_a.id)
    s3 = User(student_id="S3", email="s3@test.com", password_hash="hash", name="S3", role=UserRole.STUDENT, department_id=dept_b.id)
    db_session.add_all([s1, s2, s3])
    db_session.commit()

    total_students = 3

    # Create Elections
    # Election 1: Global (All departments)
    e1 = Election(
        title="Global Election",
        start_date=datetime.now(),
        end_date=datetime.now() + timedelta(days=1),
        status=ElectionStatus.ACTIVE,
        department_id=None
    )

    # Election 2: Department A only
    e2 = Election(
        title="Dept A Election",
        start_date=datetime.now(),
        end_date=datetime.now() + timedelta(days=1),
        status=ElectionStatus.ACTIVE,
        department_id=dept_a.id
    )

    db_session.add_all([e1, e2])
    db_session.commit()

    # Create Candidate for Global Election
    c1 = Candidate(
        election_id=e1.id,
        name="Candidate 1",
        role="Role 1",
        photo_url="http://example.com/photo.jpg",
        manifesto="Manifesto"
    )
    db_session.add(c1)
    db_session.commit()

    # Cast 1 vote in Global Election
    vote = Vote(election_id=e1.id, user_id=s1.id, candidate_id=c1.id)
    db_session.add(vote)
    db_session.commit()

    # Call the API
    response = client.get("/dashboard/stats")
    assert response.status_code == 200
    data = response.json()

    # Expected calculation:
    # E1 eligible: 3 (all students)
    # E2 eligible: 2 (Dept A students only)
    # Total eligible: 3 + 2 = 5
    # Total votes: 1
    # Turnout: 1/5 * 100 = 20.0

    # Current (Buggy) calculation:
    # Total students * Num elections = 3 * 2 = 6
    # Turnout: 1/6 * 100 = 16.7

    print(f"Turnout: {data['voter_turnout']}")

    # Assert correct behavior (this should fail initially)
    # 20.0 is correct
    assert data["voter_turnout"] == 20.0
