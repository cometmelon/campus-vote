import pytest
from unittest.mock import MagicMock
from services.queue_service import create_voting_queue_entries
from models import Election, User, VotingQueue

def test_create_voting_queue_entries_empty_students():
    """
    Test creating voting queue entries with an empty list of students.
    Should return (0, 0) and handle the edge case gracefully.
    """
    # Mock database session
    mock_db = MagicMock()

    # Mock election
    mock_election = MagicMock(spec=Election)
    mock_election.id = "election-123"

    # Empty list of students
    students = []

    # Call function
    total_batches, first_batch_count = create_voting_queue_entries(
        mock_db,
        mock_election,
        students,
        10
    )

    # Assertions
    assert total_batches == 0
    assert first_batch_count == 0

    # Verify no database entries were added
    mock_db.add.assert_not_called()

    # Verify commit was called (as per current implementation it is called unconditionally)
    mock_db.commit.assert_called_once()

def test_create_voting_queue_entries_with_students():
    """
    Test creating voting queue entries with a list of students.
    Should create entries and return correct batch counts.
    """
    # Mock database session
    mock_db = MagicMock()

    # Mock query to return None (no existing entries)
    # The code calls: db.query(VotingQueue).filter(...).first()
    # We need to ensure that the chain of calls works and returns None
    mock_query = MagicMock()
    mock_filter = MagicMock()

    mock_db.query.return_value = mock_query
    mock_query.filter.return_value = mock_filter
    mock_filter.first.return_value = None

    # Mock election
    mock_election = MagicMock(spec=Election)
    mock_election.id = "election-123"

    # Mock students
    student1 = MagicMock(spec=User)
    student1.id = "student-1"
    student2 = MagicMock(spec=User)
    student2.id = "student-2"
    students = [student1, student2]

    # Call function with batch_size=1 so each student is in a separate batch
    # total_students=2, batch_size=1 -> total_batches=2
    # Batch 1: student-1 (i=0, batch=1) -> first_batch_count increments
    # Batch 2: student-2 (i=1, batch=2) -> first_batch_count does not increment
    total_batches, first_batch_count = create_voting_queue_entries(
        mock_db,
        mock_election,
        students,
        1
    )

    # Assertions
    assert total_batches == 2
    assert first_batch_count == 1

    # Verify database entries were added
    assert mock_db.add.call_count == 2
    mock_db.commit.assert_called_once()
