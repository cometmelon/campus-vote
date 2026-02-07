import sys
import os
import threading
import concurrent.futures
import time
import uuid
import secrets
from datetime import datetime, timedelta

# Add backend directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Override database to use a file-based SQLite db for concurrency testing
TEST_DB_URL = "sqlite:///./test_race.db"
os.environ["DATABASE_URL"] = TEST_DB_URL

# Import app after setting env var
from main import app
from database import Base, get_db
from models import Election, Candidate, User, UserRole, VotingQueue, QueueStatus, Vote

# Setup database
engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

def setup_test_data():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()

    # Create election
    election_id = uuid.uuid4()
    election = Election(
        id=election_id,
        title="Test Election",
        status="active",
        start_date=datetime.now(),
        end_date=datetime.now() + timedelta(days=1)
    )
    db.add(election)

    # Create candidate
    candidate_id = uuid.uuid4()
    candidate = Candidate(
        id=candidate_id,
        election_id=election_id,
        name="Test Candidate",
        role="President"
    )
    db.add(candidate)

    # Create users and queue entries
    tokens = []
    num_voters = 50

    for i in range(num_voters):
        user_id = uuid.uuid4()
        user = User(
            id=user_id,
            student_id=f"student_{i}",
            email=f"student_{i}@example.com",
            name=f"Student {i}",
            role=UserRole.STUDENT,
            password_hash="hashed_secret"
        )
        db.add(user)

        token = secrets.token_urlsafe(32)
        queue_entry = VotingQueue(
            id=uuid.uuid4(),
            election_id=election_id,
            user_id=user_id,
            status=QueueStatus.NOTIFIED,
            voting_token=token,
            batch_number=1
        )
        db.add(queue_entry)
        tokens.append(token)

    db.commit()
    db.close()

    return election_id, candidate_id, tokens

def cast_vote(token, election_id, candidate_id):
    try:
        response = client.post(
            f"/voting/cast/{token}",
            json={
                "election_id": str(election_id),
                "candidate_id": str(candidate_id)
            }
        )
        return response.status_code
    except Exception as e:
        print(f"Error voting: {e}")
        return 500

def run_test():
    print("Setting up test data...")
    election_id, candidate_id, tokens = setup_test_data()

    print(f"Starting concurrent voting simulation with {len(tokens)} voters...")

    start_time = time.time()

    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        futures = [
            executor.submit(cast_vote, token, election_id, candidate_id)
            for token in tokens
        ]
        results = [f.result() for f in concurrent.futures.as_completed(futures)]

    duration = time.time() - start_time
    print(f"Voting completed in {duration:.2f} seconds")

    # Verify results
    db = TestingSessionLocal()
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    vote_count = candidate.vote_count

    actual_votes = db.query(Vote).filter(Vote.candidate_id == candidate_id).count()

    print(f"Expected votes: {len(tokens)}")
    print(f"Actual votes in DB table: {actual_votes}")
    print(f"Candidate vote_count field: {vote_count}")

    db.close()

    if vote_count != len(tokens):
        print("❌ RACE CONDITION DETECTED!")
        print(f"Lost {len(tokens) - vote_count} votes in the counter.")
        return False
    else:
        print("✅ No race condition detected. Count matches.")
        return True

if __name__ == "__main__":
    success = run_test()
    sys.exit(0 if success else 1)
