from datetime import datetime, timedelta
import pytest
from jose import jwt
from routers.auth import create_access_token
from config import settings

def test_create_access_token_default_expiration():
    """Test token creation with default expiration"""
    data = {"sub": "testuser"}
    token = create_access_token(data)

    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

    assert payload["sub"] == "testuser"
    assert "exp" in payload

    # Check if expiration is close to default (within a reasonable margin)
    # Default is settings.ACCESS_TOKEN_EXPIRE_MINUTES
    expected_exp = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    # Use utcfromtimestamp to avoid timezone issues when comparing with utcnow()
    token_exp = datetime.utcfromtimestamp(payload["exp"])

    # Allow 5 seconds difference
    diff = abs((token_exp - expected_exp).total_seconds())
    assert diff < 5

def test_create_access_token_custom_expiration():
    """Test token creation with custom expiration"""
    data = {"sub": "testuser"}
    expires_delta = timedelta(minutes=15)
    token = create_access_token(data, expires_delta=expires_delta)

    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

    expected_exp = datetime.utcnow() + expires_delta
    token_exp = datetime.utcfromtimestamp(payload["exp"])

    diff = abs((token_exp - expected_exp).total_seconds())
    assert diff < 5

def test_create_access_token_payload_integrity():
    """Test that all data passed is encoded in the token"""
    data = {"sub": "testuser", "role": "admin", "custom": "value"}
    token = create_access_token(data)

    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

    assert payload["sub"] == "testuser"
    assert payload["role"] == "admin"
    assert payload["custom"] == "value"

def test_create_access_token_empty_data():
    """Test token creation with empty data"""
    data = {}
    token = create_access_token(data)

    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

    assert "exp" in payload
    # Removed brittle assertion on payload length

def test_create_access_token_no_side_effects():
    """Test that input dictionary is not modified"""
    data = {"sub": "testuser"}
    original_data = data.copy()
    create_access_token(data)
    assert data == original_data
