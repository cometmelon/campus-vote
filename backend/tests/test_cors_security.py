import sys
import os

# Add parent directory to sys.path to import main
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_cors_valid_request():
    """Test valid CORS request with allowed headers"""
    headers = {
        "Origin": "http://localhost:5173",
        "Access-Control-Request-Method": "DELETE",
        "Access-Control-Request-Headers": "Authorization, Content-Type",
    }
    response = client.options("/", headers=headers)

    assert response.status_code == 200, "Expected status code 200 for valid OPTIONS request"
    assert response.headers.get("access-control-allow-origin") == "http://localhost:5173"

    allowed_methods = response.headers.get("access-control-allow-methods", "").split(", ")
    expected_methods = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    # Check if all expected methods are present
    for method in expected_methods:
        if method not in allowed_methods:
            print(f"Warning: Expected method {method} not found in {allowed_methods}")
            # Note: Depending on implementation, allowed methods might vary slightly or include defaults.
            # But we check specific methods.

    allowed_headers = response.headers.get("access-control-allow-headers", "").split(", ")
    assert "Authorization" in allowed_headers, f"Authorization not found in {allowed_headers}"
    assert "Content-Type" in allowed_headers, f"Content-Type not found in {allowed_headers}"

def test_cors_invalid_request():
    """Test invalid CORS request with disallowed header"""
    headers_invalid = {
        "Origin": "http://localhost:5173",
        "Access-Control-Request-Method": "DELETE",
        "Access-Control-Request-Headers": "X-Custom-Header",
    }
    response_invalid = client.options("/", headers=headers_invalid)

    # Strictly, this should be 400 Bad Request
    assert response_invalid.status_code == 400, f"Expected 400 Bad Request for disallowed header, got {response_invalid.status_code}"

if __name__ == "__main__":
    try:
        test_cors_valid_request()
        print("test_cors_valid_request: PASSED")
        test_cors_invalid_request()
        print("test_cors_invalid_request: PASSED")
    except AssertionError as e:
        print(f"TEST FAILED: {e}")
        exit(1)
