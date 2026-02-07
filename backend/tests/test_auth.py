import sys
import os
from datetime import datetime, timedelta, timezone
from jose import jwt
import pytest

# Add backend to sys.path so we can import routers and config
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from routers.auth import create_access_token
from config import settings

def test_create_access_token():
    data = {"sub": "testuser"}
    token = create_access_token(data)

    assert token is not None

    decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    assert decoded["sub"] == "testuser"
    assert "exp" in decoded

    # Check expiry (naive vs aware check might be tricky here depending on implementation)
    # The current implementation uses datetime.utcnow() which is naive.
    # The timestamp in JWT is always UTC seconds since epoch.

    now_ts = datetime.now(timezone.utc).timestamp()
    expected_exp_seconds = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60

    # Allow 5 seconds tolerance
    assert abs(decoded["exp"] - (now_ts + expected_exp_seconds)) < 5

def test_create_access_token_custom_expiry():
    data = {"sub": "testuser"}
    expires_delta = timedelta(minutes=10)
    token = create_access_token(data, expires_delta=expires_delta)

    decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

    now_ts = datetime.now(timezone.utc).timestamp()
    expected_exp_seconds = 10 * 60

    # Allow 5 seconds tolerance
    assert abs(decoded["exp"] - (now_ts + expected_exp_seconds)) < 5
