import sys
import os
import pytest

# Add backend directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from routers.auth import get_password_hash, verify_password

def test_get_password_hash_basic():
    """Test that get_password_hash returns a string and is not empty."""
    password = "secret_password"
    hashed = get_password_hash(password)
    assert isinstance(hashed, str)
    assert len(hashed) > 0

def test_get_password_hash_salt():
    """Test that get_password_hash generates different hashes for the same password."""
    password = "secret_password"
    hash1 = get_password_hash(password)
    hash2 = get_password_hash(password)
    assert hash1 != hash2

def test_verify_password_success():
    """Test that verify_password returns True for correct password and hash."""
    password = "secret_password"
    hashed = get_password_hash(password)
    assert verify_password(password, hashed) is True

def test_verify_password_failure():
    """Test that verify_password returns False for incorrect password."""
    password = "secret_password"
    hashed = get_password_hash(password)
    assert verify_password("wrong_password", hashed) is False

def test_get_password_hash_empty():
    """Test that get_password_hash handles empty string."""
    password = ""
    hashed = get_password_hash(password)
    assert isinstance(hashed, str)
    assert len(hashed) > 0
    assert verify_password(password, hashed) is True

def test_get_password_hash_unicode():
    """Test that get_password_hash handles unicode characters."""
    password = "🔒secret_password_🚀"
    hashed = get_password_hash(password)
    assert isinstance(hashed, str)
    assert len(hashed) > 0
    assert verify_password(password, hashed) is True
