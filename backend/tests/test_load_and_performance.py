import time
import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

AUTH_HEADER = {
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIwMDAwMDAwMC0wMDAwLTAwMDAtMDAwMC0wMDAwMDAwMDAwMDEiLCJlbWFpbCI6InVzZXIxQGV4YW1wbGUuY29tIiwicm9sZSI6ImF1dGhlbnRpYXRlZCJ9.Dx9cvnLGMzsbCfrQ3jZzepEjsepkrsOiZVPlCUpSIuQ"
}

PREDICT_PAYLOAD = {
    "age": 30.0,
    "bmi": 22.5,
    "symptoms_count": 2,
    "has_fatigue": True,
    "has_pale_skin": True,
    "hemoglobin_g_dl": 11.2,
    "serum_vitamin_d_ng_ml": 22.0,
    "serum_vitamin_b12_pg_ml": 260.0
}

# --- Supabase Mock Fixture for Performance Isolation ---
class FakeSupabaseResponse:
    def __init__(self, data):
        self.data = data

class FakeSupabaseQuery:
    def __init__(self, db_store, table_name):
        self.db_store = db_store
        self.table_name = table_name
        self.filters = {}
        self.order_field = None
        self.order_desc = False
        self.insert_data = None

    def select(self, *args, **kwargs):
        return self

    def eq(self, field, value):
        self.filters[field] = value
        return self

    def gte(self, field, value):
        self.filters[f"{field}__gte"] = value
        return self

    def order(self, field, desc=False):
        self.order_field = field
        self.order_desc = desc
        return self

    def insert(self, payload):
        self.insert_data = payload
        return self

    def execute(self):
        records = self.db_store.setdefault(self.table_name, [])
        if self.insert_data is not None:
            rec = dict(self.insert_data)
            rec["id"] = f"id_{len(records) + 1}"
            records.append(rec)
            return FakeSupabaseResponse([rec])

        filtered = []
        for r in records:
            match = True
            for k, v in self.filters.items():
                if k.endswith("__gte"):
                    real_k = k[:-5]
                    if r.get(real_k, "") < v:
                        match = False
                        break
                elif r.get(k) != v:
                    match = False
                    break
            if match:
                filtered.append(r)

        if self.order_field:
            filtered.sort(key=lambda x: x.get(self.order_field, ""), reverse=self.order_desc)

        return FakeSupabaseResponse(filtered)

class FakeSupabaseClient:
    def __init__(self, db_store):
        self.db_store = db_store

    def table(self, name):
        return FakeSupabaseQuery(self.db_store, name)

@pytest.fixture(autouse=True)
def mock_perf_supabase():
    db_store = {
        "prediction_history": [],
        "symptom_assessments": [],
        "blood_test_results": []
    }
    fake_client = FakeSupabaseClient(db_store)
    with patch("app.services.prediction_history_service.get_supabase_admin_client", return_value=fake_client):
        yield db_store


# ============================================================================
# 1. API RESPONSE LATENCY BENCHMARKS (< 5000ms SLA for cold start, < 1000ms for warm)
# ============================================================================
def test_prediction_endpoint_latency():
    """Verify POST /api/v1/predict responds within performance threshold (< 1000ms)."""
    start_time = time.perf_counter()
    res = client.post("/api/v1/predict", json=PREDICT_PAYLOAD, headers=AUTH_HEADER)
    latency_ms = (time.perf_counter() - start_time) * 1000

    assert res.status_code == 200
    assert latency_ms < 1000, f"Prediction endpoint latency too high: {latency_ms:.2f} ms"

def test_recommendation_endpoint_latency():
    """Verify POST /api/v1/recommendations responds within cold/warm SLA thresholds (< 5000ms)."""
    payload = {
        "predicted_class": "Anemia",
        "risk_level": "High Risk",
        "risk_score": 80.0,
        "dietary_preference": "vegetarian",
        "limit": 10
    }
    start_time = time.perf_counter()
    res = client.post("/api/v1/recommendations", json=payload, headers=AUTH_HEADER)
    latency_ms = (time.perf_counter() - start_time) * 1000

    assert res.status_code == 200
    assert latency_ms < 5000, f"Recommendation endpoint latency too high: {latency_ms:.2f} ms"

def test_meal_plan_generation_latency():
    """Verify POST /api/v1/meal-plans/generate responds within SLA threshold (< 5000ms)."""
    payload = {
        "recommendation_request": {
            "predicted_class": "Anemia",
            "risk_level": "High Risk",
            "risk_score": 80.0,
            "dietary_preference": "vegetarian",
            "limit": 20
        }
    }
    start_time = time.perf_counter()
    res = client.post("/api/v1/meal-plans/generate", json=payload, headers=AUTH_HEADER)
    latency_ms = (time.perf_counter() - start_time) * 1000

    assert res.status_code == 200
    assert latency_ms < 5000, f"Meal plan generation latency too high: {latency_ms:.2f} ms"

def test_recipe_search_latency():
    """Verify GET /api/v1/recipes/search responds within performance threshold (< 1000ms)."""
    start_time = time.perf_counter()
    res = client.get("/api/v1/recipes/search?query=spinach&limit=10", headers=AUTH_HEADER)
    latency_ms = (time.perf_counter() - start_time) * 1000

    assert res.status_code == 200
    assert latency_ms < 1000, f"Recipe search latency too high: {latency_ms:.2f} ms"


# ============================================================================
# 2. CONCURRENT LOAD SIMULATION (Burst execution)
# ============================================================================
def test_simulated_burst_load():
    """Simulates 50 sequential prediction requests under sustained load."""
    total_requests = 50
    start_total = time.perf_counter()

    for i in range(total_requests):
        resp = client.post("/api/v1/predict", json=PREDICT_PAYLOAD, headers=AUTH_HEADER)
        assert resp.status_code == 200

    total_duration = time.perf_counter() - start_total
    avg_latency_ms = (total_duration / total_requests) * 1000

    assert avg_latency_ms < 300, f"Average latency under burst load too high: {avg_latency_ms:.2f} ms per request"
