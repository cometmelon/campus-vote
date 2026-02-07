import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Add backend to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock missing dependencies
mock_sqlalchemy = MagicMock()
sys.modules["sqlalchemy"] = mock_sqlalchemy
sys.modules["sqlalchemy.orm"] = MagicMock()
sys.modules["sqlalchemy.ext.declarative"] = MagicMock()

# Mock models and config
mock_models = MagicMock()
sys.modules["models"] = mock_models
mock_config = MagicMock()
sys.modules["config"] = mock_config
mock_config.settings.VOTING_LINK_EXPIRE_HOURS = 24

# Import the service after mocking
from services.queue_service import create_voting_queue_entries

class TestQueueService(unittest.TestCase):
    def setUp(self):
        self.db = MagicMock()
        self.election = MagicMock()
        self.election.id = "election-id"
        self.batch_size = 10

    def test_create_voting_queue_entries_empty_students(self):
        """Test with empty student list"""
        students = []
        total_batches, first_batch_count = create_voting_queue_entries(
            self.db, self.election, students, self.batch_size
        )

        self.assertEqual(total_batches, 0)
        self.assertEqual(first_batch_count, 0)
        self.db.commit.assert_called_once()

    def test_create_voting_queue_entries_with_students(self):
        """Test with students and batching"""
        students = [MagicMock(id=f"student-{i}") for i in range(25)]

        # Mock db.query().filter().first() to return None (no existing entries)
        self.db.query().filter().first.return_value = None

        total_batches, first_batch_count = create_voting_queue_entries(
            self.db, self.election, students, self.batch_size
        )

        self.assertEqual(total_batches, 3) # 25 / 10 -> ceil(2.5) = 3
        self.assertEqual(first_batch_count, 10) # First batch should have 10
        self.assertEqual(self.db.add.call_count, 25)
        self.db.commit.assert_called_once()

    def test_create_voting_queue_entries_duplicate_prevention(self):
        """Test that existing entries are not recreated"""
        students = [MagicMock(id="student-1")]

        # Mock db.query().filter().first() to return an existing entry
        self.db.query().filter().first.return_value = MagicMock()

        total_batches, first_batch_count = create_voting_queue_entries(
            self.db, self.election, students, self.batch_size
        )

        self.assertEqual(total_batches, 1)
        self.assertEqual(first_batch_count, 0) # Already exists, so not in first batch count
        self.db.add.assert_not_called()
        self.db.commit.assert_called_once()

    def test_create_voting_queue_entries_invalid_batch_size(self):
        """Test with zero or negative batch size"""
        students = [MagicMock(id="student-1")]

        # Test zero
        total_batches, first_batch_count = create_voting_queue_entries(
            self.db, self.election, students, 0
        )
        self.assertEqual(total_batches, 0)
        self.assertEqual(first_batch_count, 0)

        # Test negative
        total_batches, first_batch_count = create_voting_queue_entries(
            self.db, self.election, students, -5
        )
        self.assertEqual(total_batches, 0)
        self.assertEqual(first_batch_count, 0)

if __name__ == "__main__":
    unittest.main()
