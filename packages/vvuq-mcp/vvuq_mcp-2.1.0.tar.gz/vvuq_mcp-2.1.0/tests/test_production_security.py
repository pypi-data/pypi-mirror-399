import pytest
import requests
import os
import time
from vvuq import VVUQClient, AuthenticationError

# Configuration
API_URL = os.getenv("VVUQ_API_URL", "http://localhost:8081")
VALID_KEY = os.getenv("VVUQ_API_KEY", "e3e0506d293ab30dd243f7179150af0e7d7f3842f28745a0b2aa02049348a8d3")
INVALID_KEY = "invalid_key_123"

@pytest.fixture
def client_no_auth():
    """Client without headers"""
    return requests.Session()

@pytest.fixture
def client_bad_auth():
    """Client with invalid key"""
    s = requests.Session()
    s.headers.update({"X-API-Key": INVALID_KEY})
    return s

@pytest.fixture
def client_valid_auth():
    """Client with valid key"""
    s = requests.Session()
    s.headers.update({"X-API-Key": VALID_KEY})
    return s

@pytest.mark.integration
class TestProductionSecurity:
    """
    Security and Integrity Tests for Production Deployment.
    Requires running server at API_URL.
    """

    def test_health_check_public(self, client_no_auth):
        """Health check should be public"""
        resp = client_no_auth.get(f"{API_URL}/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "healthy"

    def test_auth_enforcement_missing_header(self, client_no_auth):
        """Protected endpoint should fail without header"""
        resp = client_no_auth.get(f"{API_URL}/contracts/test")
        # FastAPI returns 403 or 401 depending on mechanism
        assert resp.status_code in [401, 403], f"Allowed access without key! {resp.status_code}"

    def test_auth_enforcement_invalid_key(self, client_bad_auth):
        """Protected endpoint should fail with bad key"""
        resp = client_bad_auth.get(f"{API_URL}/contracts/test")
        assert resp.status_code in [401, 403], f"Allowed access with bad key! {resp.status_code}"

    def test_cors_policy(self):
        """CORS should block unauthorized origins"""
        headers = {
            "Origin": "http://evil-site.com",
            "Access-Control-Request-Method": "POST"
        }
        resp = requests.options(f"{API_URL}/contracts", headers=headers)
        
        allow_origin = resp.headers.get("Access-Control-Allow-Origin")
        assert allow_origin != "http://evil-site.com", "CORS leaked to evil-site.com"
        assert allow_origin != "*", "CORS allowed wildcard *"

    def test_rate_limiting(self, client_valid_auth):
        """
        Verify rate limiting works.
        NOTE: This test consumes quota. Run carefully.
        """
        # We need to hit the limit. Limit is 20/min/IP for /contracts
        payload = {
            "title": "Rate Limit Test",
            "description": "Pytest Spam",
            "claims": [{
                "claim_id": 1,
                "theorem": "theorem t : 1=1 := rfl",
                "payment_amount": 10.0
            }],
            "issuer_agent_id": "pytest"
        }
        
        success_count = 0
        blocked = False
        
        # Send up to 25 requests
        for _ in range(25):
            resp = client_valid_auth.post(f"{API_URL}/contracts", json=payload)
            if resp.status_code == 201:
                success_count += 1
            elif resp.status_code == 429:
                blocked = True
                break
        
        assert blocked, f"Rate limit failed! Accepted {success_count} requests without block."
        assert success_count <= 22, f"Allowed significantly more than 20 requests ({success_count})"

@pytest.mark.integration
class TestSDKProductionFlow:
    """Test using the actual SDK client"""

    def test_sdk_connection(self):
        """Test connection via SDK wrapper"""
        client = VVUQClient(api_key=VALID_KEY, base_url=API_URL)
        health = client.health()
        assert health["status"] == "healthy"

    def test_feedback_submission_sdk(self):
        """Test the new feedback endpoint via SDK"""
        client = VVUQClient(api_key=VALID_KEY, base_url=API_URL)
        resp = client.submit_feedback(
            title="Pytest Automated Feedback",
            description="Testing feedback submission from pytest suite",
            feedback_type="general",
            severity="low",
            submitter_type="automated_system"
        )
        assert resp["success"] is True
        assert "feedback_id" in resp
        assert "message" in resp
        
        # Verify message format if GitHub creation happened
        if resp.get("github_issue_created"):
            msg_lower = resp["message"].lower()
            # Expect "Ticket #123 Created" or similar
            assert "ticket #" in msg_lower or "github issue" in msg_lower
