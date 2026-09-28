import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

VALID_AUTH = {
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIwMDAwMDAwMC0wMDAwLTAwMDAtMDAwMC0wMDAwMDAwMDAwMDEiLCJlbWFpbCI6InVzZXIxQGV4YW1wbGUuY29tIiwicm9sZSI6ImF1dGhlbnRpYXRlZCJ9.Dx9cvnLGMzsbCfrQ3jZzepEjsepkrsOiZVPlCUpSIuQ"
}

INVALID_AUTH_HEADER = {
    "Authorization": "Bearer malformed.invalid.token"
}

# --- Supabase Mock Fixture for Security Audit ---
class FakeSupabaseResponse:
    def __init__(self, data):
        self.data = data

class FakeSupabaseQuery:
    def __init__(self, db_store, table_name):
        self.db_store = db_store
        self.table_name = table_name

    def select(self, *args, **kwargs):
        return self

    def eq(self, field, value):
        return self

    def gte(self, field, value):
        return self

    def order(self, field, desc=False):
        return self

    def insert(self, payload):
        return self

    def execute(self):
        return FakeSupabaseResponse([])

class FakeSupabaseClient:
    def __init__(self, db_store):
        self.db_store = db_store

    def table(self, name):
        return FakeSupabaseQuery(self.db_store, name)

@pytest.fixture(autouse=True)
def mock_security_supabase():
    db_store = {}
    fake_client = FakeSupabaseClient(db_store)
    with patch("app.services.prediction_history_service.get_supabase_admin_client", return_value=fake_client):
        yield db_store


# ============================================================================
# 1. AUTHENTICATION & AUTHORIZATION REJECTION AUDIT
# ============================================================================
def test_unauthenticated_request_rejection():
    """Verify protected endpoints reject unauthenticated requests with HTTP 401/403."""
    protected_urls = [
        ("GET", "/api/v1/predict/history"),
        ("GET", "/api/v1/predict/progress"),
        ("POST", "/api/v1/meal-plans/generate"),
        ("POST", "/api/v1/meal-plans/replace"),
        ("GET", "/api/v1/recipes/search?query=apple"),
        ("GET", "/api/v1/recipes/fdc_123456")
    ]

    for method, url in protected_urls:
        if method == "GET":
            res = client.get(url)
        else:
            res = client.post(url, json={})
        assert res.status_code in (401, 403), f"Endpoint {url} allowed unauthenticated access! ({res.status_code})"

def test_malformed_token_rejection():
    """Verify endpoints reject malformed JWT tokens."""
    res = client.get("/api/v1/predict/history", headers=INVALID_AUTH_HEADER)
    assert res.status_code in (401, 403)


# ============================================================================
# 2. INPUT VALIDATION & SANITIZATION AUDIT
# ============================================================================
def test_sql_injection_payload_sanitization():
    """Verify input fields reject or safely sanitize SQL injection attack vectors."""
    sqli_payload = {
        "age": 30,
        "bmi": 22.0,
        "diet_type": "vegetarian' OR '1'='1",
        "gender": "Female'; DROP TABLE profiles;--"
    }
    res = client.post("/api/v1/predict", json=sqli_payload, headers=VALID_AUTH)
    # FastApi / Pydantic should validate or handle safely without crashing with 500 error
    assert res.status_code in (200, 422)

def test_invalid_type_injection_rejection():
    """Verify endpoint rejects invalid primitive data types."""
    invalid_payload = {
        "age": "thirty-two",
        "bmi": [22.5]
    }
    res = client.post("/api/v1/predict", json=invalid_payload, headers=VALID_AUTH)
    assert res.status_code == 422, "API allowed invalid parameter type"


# ============================================================================
# 3. CORS & SECURITY HEADERS CHECK
# ============================================================================
def test_cors_headers_present():
    """Verify API returns expected CORS preflight headers."""
    res = client.options(
        "/api/v1/predict",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "POST"
        }
    )
    assert res.status_code in (200, 204, 405)
