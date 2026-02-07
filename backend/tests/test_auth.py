import pytest
import sys
import os

# Add parent directory to path to allow imports from backend root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from routers.auth import verify_password, get_password_hash

def test_verify_password_correct():
    """Test that verify_password returns True for correct password"""
    password = "securepassword123"
    hashed = get_password_hash(password)
    assert verify_password(password, hashed) is True

def test_verify_password_incorrect():
    """Test that verify_password returns False for incorrect password"""
    password = "securepassword123"
    hashed = get_password_hash(password)
    assert verify_password("wrongpassword", hashed) is False

def test_verify_password_empty():
    """Test verification with empty password"""
    password = ""
    # bcrypt handles empty password just fine, it hashes it like any other string
    hashed = get_password_hash(password)
    assert verify_password("", hashed) is True
    assert verify_password("something", hashed) is False

def test_verify_password_special_chars():
    """Test verification with special characters"""
    password = "passw@rd!#$%"
    hashed = get_password_hash(password)
    assert verify_password(password, hashed) is True

def test_verify_password_unicode():
    """Test verification with unicode characters"""
    password = "パスワード" # "password" in Japanese
    hashed = get_password_hash(password)
    assert verify_password(password, hashed) is True
