import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

AUTH_HEADER = {
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIwMDAwMDAwMC0wMDAwLTAwMDAtMDAwMC0wMDAwMDAwMDAwMDEiLCJlbWFpbCI6InVzZXJAZXhhbXBsZS5jb20iLCJyb2xlIjoiYXV0aGVudGljYXRlZCJ9.Dx9cvnLGMzsbCfrQ3jZzepEjsepkrsOiZVPlCUpSIuQ"
}

PREDICT_PAYLOAD = {
    "age": 30,
    "bmi": 22.0,
    "symptoms_count": 2,
    "has_fatigue": True,
    "has_brittle_nails": True,
    "hemoglobin_g_dl": 11.5
}

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
def mock_api_supabase():
    db_store = {"prediction_history": [], "symptom_assessments": [], "blood_test_results": []}
    fake_client = FakeSupabaseClient(db_store)
    with patch("app.services.prediction_history_service.get_supabase_admin_client", return_value=fake_client):
        yield db_store

def test_authenticated_prediction_history_get():
    # Execute prediction to generate snapshot
    client.post("/api/v1/predict", json=PREDICT_PAYLOAD, headers=AUTH_HEADER)

    # Fetch history
    res = client.get("/api/v1/predict/history?weeks=4", headers=AUTH_HEADER)
    assert res.status_code == 200, res.text
    data = res.json()
    assert isinstance(data, list)

def test_unauthenticated_history_rejected():
    res = client.get("/api/v1/predict/history?weeks=4")
    assert res.status_code in (401, 403)

def test_invalid_weeks_parameter_rejected():
    res = client.get("/api/v1/predict/history?weeks=5", headers=AUTH_HEADER)
    assert res.status_code == 400
    assert "Invalid weeks parameter" in res.json()["detail"]

    res_prog = client.get("/api/v1/predict/progress?weeks=10", headers=AUTH_HEADER)
    assert res_prog.status_code == 400
    assert "Invalid weeks parameter" in res_prog.json()["detail"]

def test_authenticated_prediction_progress_get():
    res = client.get("/api/v1/predict/progress?weeks=4", headers=AUTH_HEADER)
    assert res.status_code == 200, res.text
    data = res.json()
    assert "status" in data
    assert "selected_weeks" in data
    assert data["selected_weeks"] == 4
    assert "total_snapshots" in data
    assert "chronological_history" in data

def test_prediction_progress_8_and_12_weeks():
    res8 = client.get("/api/v1/predict/progress?weeks=8", headers=AUTH_HEADER)
    assert res8.status_code == 200
    assert res8.json()["selected_weeks"] == 8

    res12 = client.get("/api/v1/predict/progress?weeks=12", headers=AUTH_HEADER)
    assert res12.status_code == 200
    assert res12.json()["selected_weeks"] == 12
