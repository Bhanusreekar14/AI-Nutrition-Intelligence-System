import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# Standard valid base64 JWT tokens for development mock authentication
USER_1_AUTH = {
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIwMDAwMDAwMC0wMDAwLTAwMDAtMDAwMC0wMDAwMDAwMDAwMDEiLCJlbWFpbCI6InVzZXIxQGV4YW1wbGUuY29tIiwicm9sZSI6ImF1dGhlbnRpYXRlZCJ9.Dx9cvnLGMzsbCfrQ3jZzepEjsepkrsOiZVPlCUpSIuQ"
}

USER_2_AUTH = {
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIwMDAwMDAwMC0wMDAwLTAwMDAtMDAwMC0wMDAwMDAwMDAwMDIiLCJlbWFpbCI6InVzZXIyQGV4YW1wbGUuY29tIiwicm9sZSI6ImF1dGhlbnRpYXRlZCJ9.Dx9cvnLGMzsbCfrQ3jZzepEjsepkrsOiZVPlCUpSIuQ"
}

PREDICT_PAYLOAD = {
    "age": 32.0,
    "bmi": 21.5,
    "symptoms_count": 3,
    "has_fatigue": True,
    "has_pale_skin": True,
    "has_muscle_weakness": True,
    "hemoglobin_g_dl": 10.8,
    "serum_vitamin_d_ng_ml": 15.0,
    "serum_vitamin_b12_pg_ml": 210.0,
    "gender": "Female",
    "diet_type": "vegetarian"
}

# --- Supabase Mock Fixture for End-to-End Pipeline Isolation ---
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
def mock_pipeline_supabase():
    db_store = {
        "prediction_history": [],
        "symptom_assessments": [],
        "blood_test_results": [],
        "health_profiles": [],
        "food_diary": []
    }
    fake_client = FakeSupabaseClient(db_store)
    with patch("app.services.prediction_history_service.get_supabase_admin_client", return_value=fake_client):
        yield db_store


# ============================================================================
# 1. COMPLETE PIPELINE END-TO-END TEST
# ============================================================================
def test_full_user_journey_pipeline():
    """
    Validates complete flow:
    Prediction -> Recommendation -> Meal Plan -> Replacement -> Recipe Search -> Progress Tracker
    """
    # Step 1: Execute Prediction
    pred_res = client.post("/api/v1/predict", json=PREDICT_PAYLOAD, headers=USER_1_AUTH)
    assert pred_res.status_code == 200, pred_res.text
    pred_data = pred_res.json()

    assert "predicted_class" in pred_data
    assert "risk_score" in pred_data
    assert "risk_level" in pred_data
    assert "explanation" in pred_data
    assert "medical_disclaimer" in pred_data
    predicted_class = pred_data["predicted_class"]
    risk_score = pred_data["risk_score"]
    risk_level = pred_data["risk_level"]

    # Step 2: Request Dietary Recommendations
    rec_payload = {
        "predicted_class": predicted_class,
        "risk_level": risk_level,
        "risk_score": risk_score,
        "dietary_preference": "vegetarian",
        "allergies_intolerances": [],
        "prohibited_foods": [],
        "limit": 10
    }
    rec_res = client.post("/api/v1/recommendations", json=rec_payload, headers=USER_1_AUTH)
    assert rec_res.status_code == 200, rec_res.text
    rec_data = rec_res.json()

    assert "recommended_foods" in rec_data
    assert len(rec_data["recommended_foods"]) > 0
    top_recommended_food = rec_data["recommended_foods"][0]["food_name"]

    # Step 3: Generate 7-Day Meal Plan
    plan_payload = {
        "recommendation_request": rec_payload
    }
    plan_res = client.post("/api/v1/meal-plans/generate", json=plan_payload, headers=USER_1_AUTH)
    assert plan_res.status_code == 200, plan_res.text
    weekly_plan = plan_res.json()

    assert "days" in weekly_plan
    assert len(weekly_plan["days"]) == 7
    assert weekly_plan["deficiency_class"] == predicted_class

    # Step 4: Meal Replacement
    day1_bf = weekly_plan["days"][0]["meals"]["breakfast"]["selected_foods"]
    target_food = day1_bf[0]["food_name"]

    replace_payload = {
        "weekly_plan": weekly_plan,
        "day": 1,
        "meal_type": "breakfast",
        "target_food_name": target_food,
        "dietary_preference": "vegetarian"
    }
    rep_res = client.post("/api/v1/meal-plans/replace", json=replace_payload, headers=USER_1_AUTH)
    assert rep_res.status_code == 200, rep_res.text
    rep_data = rep_res.json()

    assert rep_data["original_food"]["food_name"] == target_food
    assert "replacement_food" in rep_data

    # Step 5: Recipe Search & Detail Lookup
    search_query = top_recommended_food.split()[0]
    recipe_search_res = client.get(f"/api/v1/recipes/search?query={search_query}&limit=5", headers=USER_1_AUTH)
    assert recipe_search_res.status_code == 200, recipe_search_res.text
    recipes = recipe_search_res.json()["recipes"]
    assert len(recipes) > 0

    first_recipe_id = recipes[0]["recipe_id"]
    recipe_detail_res = client.get(f"/api/v1/recipes/{first_recipe_id}", headers=USER_1_AUTH)
    assert recipe_detail_res.status_code == 200, recipe_detail_res.text
    assert recipe_detail_res.json()["recipe_id"] == first_recipe_id

    # Step 6: Prediction History & Longitudinal Progress Verification
    history_res = client.get("/api/v1/predict/history?weeks=4", headers=USER_1_AUTH)
    assert history_res.status_code == 200, history_res.text
    history_entries = history_res.json()
    assert len(history_entries) >= 1
    assert history_entries[0]["predicted_class"] == predicted_class

    progress_res = client.get("/api/v1/predict/progress?weeks=4", headers=USER_1_AUTH)
    assert progress_res.status_code == 200, progress_res.text
    progress_data = progress_res.json()
    assert progress_data["selected_weeks"] == 4
    assert progress_data["total_snapshots"] >= 1


# ============================================================================
# 2. USER ISOLATION & AUTHENTICATION TESTS
# ============================================================================
def test_pipeline_user_isolation_and_security():
    """
    Verifies that User A and User B cannot access each other's data,
    and unauthenticated calls are rejected.
    """
    # User 1 makes a prediction
    client.post("/api/v1/predict", json=PREDICT_PAYLOAD, headers=USER_1_AUTH)

    # User 2 history should be empty (isolated from User 1)
    u2_hist = client.get("/api/v1/predict/history?weeks=4", headers=USER_2_AUTH)
    assert u2_hist.status_code == 200
    assert len(u2_hist.json()) == 0

    u2_prog = client.get("/api/v1/predict/progress?weeks=4", headers=USER_2_AUTH)
    assert u2_prog.status_code == 200
    assert u2_prog.json()["total_snapshots"] == 0

    # Unauthenticated calls
    assert client.get("/api/v1/predict/history?weeks=4").status_code in (401, 403)
    assert client.get("/api/v1/predict/progress?weeks=4").status_code in (401, 403)
    assert client.post("/api/v1/meal-plans/generate", json={}).status_code in (401, 403)
    assert client.post("/api/v1/meal-plans/replace", json={}).status_code in (401, 403)


# ============================================================================
# 3. EDGE CASES & INSUFFICIENT DATA HANDLING
# ============================================================================
def test_pipeline_edge_cases_and_error_handling():
    """
    Tests edge cases across pipeline modules:
    - Invalid weeks parameter
    - Non-existent recipe ID
    - Meal replacement for non-existent item
    - Insufficient history state messaging
    """
    # 1. Invalid weeks parameter
    inv_hist = client.get("/api/v1/predict/history?weeks=10", headers=USER_1_AUTH)
    assert inv_hist.status_code == 400
    assert "Invalid weeks" in inv_hist.json()["detail"]

    # 2. Non-existent recipe lookup with auth headers
    no_rec = client.get("/api/v1/recipes/fdc_999999999999", headers=USER_1_AUTH)
    assert no_rec.status_code == 404

    # 3. Insufficient history response structure for brand new user
    new_user_auth = {
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIwMDAwMDAwMC0wMDAwLTAwMDAtMDAwMC0wMDAwMDAwMDAwOTkiLCJlbWFpbCI6Im5ld0BleGFtcGxlLmNvbSIsInJvbGUiOiJhdXRoZW50aWNhdGVkIn0.Dx9cvnLGMzsbCfrQ3jZzepEjsepkrsOiZVPlCUpSIuQ"
    }
    prog_res = client.get("/api/v1/predict/progress?weeks=4", headers=new_user_auth)
    assert prog_res.status_code == 200
    data = prog_res.json()
    assert data["status"] == "insufficient_history"
    assert data["total_snapshots"] == 0
    assert "No historical deficiency-risk snapshots are available" in data["message"]


# ============================================================================
# 4. MEDICAL DISCLAIMER & DIETARY PREFERENCE CONSISTENCY
# ============================================================================
def test_pipeline_disclaimer_and_preference_consistency():
    """
    Verifies medical disclaimer presence across modules and strict adherence
    to dietary preferences (e.g. vegan) in recommendations and meal plans.
    """
    vegan_payload = dict(PREDICT_PAYLOAD)
    vegan_payload["diet_type"] = "vegan"

    pred_res = client.post("/api/v1/predict", json=vegan_payload, headers=USER_1_AUTH)
    assert pred_res.status_code == 200
    assert "medical_disclaimer" in pred_res.json()

    rec_payload = {
        "predicted_class": "Vitamin D Deficiency",
        "risk_level": "High Risk",
        "risk_score": 85.0,
        "dietary_preference": "vegan",
        "allergies_intolerances": [],
        "prohibited_foods": [],
        "limit": 10
    }
    rec_res = client.post("/api/v1/recommendations", json=rec_payload, headers=USER_1_AUTH)
    assert rec_res.status_code == 200
    rec_data = rec_res.json()
    assert "medical_disclaimer" in rec_data

    # Verify no non-vegan foods returned in recommendations
    non_vegan_items = {"Milk", "Eggs", "Cheese", "Beef", "Chicken", "Pork", "Fish"}
    for item in rec_data["recommended_foods"]:
        assert item["food_name"] not in non_vegan_items
