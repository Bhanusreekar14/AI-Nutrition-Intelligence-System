import pytest
from unittest.mock import patch
from app.services.prediction_history_service import PredictionHistoryService
from app.models.prediction import DeficiencyPredictionResponse, SHAPExplanation, FeatureContribution, DeficiencyPredictionRequest

MOCK_PREDICTION = DeficiencyPredictionResponse(
    predicted_class="Anemia",
    predicted_probability=0.85,
    risk_score=75.5,
    risk_level="High Risk",
    class_probabilities={"Anemia": 0.85, "Healthy": 0.15},
    explanation=SHAPExplanation(
        top_positive_features=[FeatureContribution(feature="hemoglobin_g_dl", contribution=1.2)],
        top_negative_features=[FeatureContribution(feature="age", contribution=-0.2)]
    ),
    medical_disclaimer="Test disclaimer"
)

MOCK_REQUEST = DeficiencyPredictionRequest(
    age=30,
    bmi=22.0,
    symptoms_count=2,
    hemoglobin_g_dl=11.5,
    serum_vitamin_d_ng_ml=25.0,
    serum_vitamin_b12_pg_ml=300.0
)

USER_1 = "00000000-0000-0000-0000-000000000001"
USER_2 = "00000000-0000-0000-0000-000000000002"

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
def mock_supabase():
    db_store = {"prediction_history": [], "symptom_assessments": [], "blood_test_results": []}
    fake_client = FakeSupabaseClient(db_store)
    with patch("app.services.prediction_history_service.get_supabase_admin_client", return_value=fake_client):
        yield db_store

def test_save_prediction_snapshot_structure():
    snapshot = PredictionHistoryService.save_prediction_snapshot(
        user_id=USER_1,
        prediction=MOCK_PREDICTION,
        req_features=MOCK_REQUEST
    )
    assert snapshot is not None
    assert snapshot["user_id"] == USER_1
    assert snapshot["predicted_class"] == "Anemia"
    assert snapshot["risk_score"] == 75.5
    assert snapshot["risk_level"] == "High Risk"
    assert snapshot["symptoms_count"] == 2
    assert snapshot["serum_hemoglobin_g_dl"] == 11.5

def test_duplicate_snapshot_protection():
    snap1 = PredictionHistoryService.save_prediction_snapshot(
        user_id=USER_1,
        prediction=MOCK_PREDICTION,
        req_features=MOCK_REQUEST
    )
    snap2 = PredictionHistoryService.save_prediction_snapshot(
        user_id=USER_1,
        prediction=MOCK_PREDICTION,
        req_features=MOCK_REQUEST
    )
    assert snap1 is not None
    assert snap2 is not None
    assert snap1["id"] == snap2["id"]

def test_history_retrieval_and_user_isolation():
    PredictionHistoryService.save_prediction_snapshot(
        user_id=USER_1,
        prediction=MOCK_PREDICTION,
        req_features=MOCK_REQUEST
    )
    history_u1 = PredictionHistoryService.get_prediction_history(USER_1, weeks=4)
    history_u2 = PredictionHistoryService.get_prediction_history(USER_2, weeks=4)

    assert isinstance(history_u1, list)
    assert len(history_u1) == 1
    assert len(history_u2) == 0

def test_invalid_weeks_parameter():
    with pytest.raises(ValueError):
        PredictionHistoryService.get_prediction_history(USER_1, weeks=5)

    with pytest.raises(ValueError):
        PredictionHistoryService.get_prediction_progress(USER_1, weeks=10)

def test_progress_calculation_empty_user():
    empty_user = "00000000-0000-0000-0000-000000000099"
    progress = PredictionHistoryService.get_prediction_progress(empty_user, weeks=4)
    assert progress["status"] == "insufficient_history"
    assert progress["total_snapshots"] == 0
    assert "No historical deficiency-risk snapshots" in progress["message"]
