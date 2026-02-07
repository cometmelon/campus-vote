import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add backend to path
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
from database import get_db, Base
from models import (
    User,
    UserRole,
    Election,
    ElectionStatus,
    Department,
    VotingQueue,
    QueueStatus,
)
from config import settings
from datetime import datetime, timedelta

# Setup test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_integration.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
def client():
    # Reset DB
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    # Patch SessionLocal in email_service to use test DB for background tasks
    with patch("services.email_service.SessionLocal", TestingSessionLocal):
        with TestClient(app) as c:
            yield c
            import os

            (
                os.remove("test_integration.db")
                if os.path.exists("test_integration.db")
                else None
            )


@pytest.fixture
def setup_data():
    db = TestingSessionLocal()
    # Create Admin
    admin = User(
        student_id="admin",
        email="admin@example.com",
        password_hash="hashed_password",
        name="Admin User",
        role=UserRole.ADMIN,
    )
    db.add(admin)

    # Create Department
    dept = Department(name="Computer Science", code="CS")
    db.add(dept)
    db.commit()

    # Create Students
    for i in range(5):
        student = User(
            student_id=f"student{i}",
            email=f"student{i}@example.com",
            password_hash="hashed_password",
            name=f"Student {i}",
            role=UserRole.STUDENT,
            department_id=dept.id,
        )
        db.add(student)

    # Create Election
    election = Election(
        title="Test Election",
        start_date=datetime.utcnow(),
        end_date=datetime.utcnow() + timedelta(hours=1),
        status=ElectionStatus.ACTIVE,
        department_id=dept.id,
    )
    db.add(election)
    db.commit()

    data = {"election_id": str(election.id), "admin_id": str(admin.id)}
    db.close()
    return data


def test_send_voting_links_integration(client, setup_data):
    # Override admin user dependency
    from routers.auth import get_admin_user

    # We need to return a User object that behaves like an admin
    admin_user = User(id=setup_data["admin_id"], role=UserRole.ADMIN)
    app.dependency_overrides[get_admin_user] = lambda: admin_user

    # Mock resend
    with patch("resend.Emails.send") as mock_send:
        mock_send.return_value = {"id": "test_id"}
        # Patch settings.RESEND_API_KEY to trigger email sending logic
        with patch.object(settings, "RESEND_API_KEY", "test_key"):
            response = client.post(
                "/voting/send-links",
                json={"election_id": setup_data["election_id"], "batch_size": 10},
            )

            assert response.status_code == 200
            # With TestClient, background tasks run synchronously after request but before client returns
            # So we expect emails to be sent
            assert mock_send.call_count == 5
            assert "emails scheduled for sending" in response.json()["message"]

    # Verify DB status
    db = TestingSessionLocal()
    entries = (
        db.query(VotingQueue).filter(VotingQueue.status == QueueStatus.NOTIFIED).all()
    )
    assert len(entries) == 5
    db.close()
