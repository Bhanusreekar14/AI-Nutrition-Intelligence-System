import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

AUTH_HEADER = {
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIwMDAwMDAwMC0wMDAwLTAwMDAtMDAwMC0wMDAwMDAwMDAwMDEiLCJlbWFpbCI6InVzZXJAZXhhbXBsZS5jb20iLCJyb2xlIjoiYXV0aGVudGljYXRlZCJ9.Dx9cvnLGMzsbCfrQ3jZzepEjsepkrsOiZVPlCUpSIuQ"
}

GENERATE_PAYLOAD = {
    "recommendation_request": {
        "predicted_class": "Anemia",
        "risk_level": "High Risk",
        "risk_score": 80.0,
        "dietary_preference": "vegetarian",
        "allergies_intolerances": ["gluten"],
        "prohibited_foods": ["beef"],
        "limit": 50
    }
}

def test_authenticated_meal_plan_generation():
    response = client.post("/api/v1/meal-plans/generate", json=GENERATE_PAYLOAD, headers=AUTH_HEADER)
    assert response.status_code == 200, response.text
    data = response.json()
    assert "days" in data
    assert len(data["days"]) == 7
    assert data["total_days"] == 7
    assert data["deficiency_class"] == "Anemia"

def test_unauthenticated_generation_request_rejected():
    response = client.post("/api/v1/meal-plans/generate", json=GENERATE_PAYLOAD)
    assert response.status_code in {401, 403}

def test_valid_generation_request_structure():
    response = client.post("/api/v1/meal-plans/generate", json=GENERATE_PAYLOAD, headers=AUTH_HEADER)
    data = response.json()
    for day_plan in data["days"]:
        assert "day" in day_plan
        assert "meals" in day_plan
        assert "breakfast" in day_plan["meals"]
        assert "lunch" in day_plan["meals"]
        assert "snack" in day_plan["meals"]
        assert "dinner" in day_plan["meals"]
        assert "total_calories" in day_plan

def test_invalid_generation_request_handling():
    invalid_payload = {"recommendation_request": {"risk_score": "not_a_number"}}
    response = client.post("/api/v1/meal-plans/generate", json=invalid_payload, headers=AUTH_HEADER)
    assert response.status_code == 422

def test_authenticated_meal_replacement():
    # 1. Generate plan
    gen_resp = client.post("/api/v1/meal-plans/generate", json=GENERATE_PAYLOAD, headers=AUTH_HEADER)
    assert gen_resp.status_code == 200
    weekly_plan = gen_resp.json()

    # Pick a food item from Day 1 Breakfast
    day1_bf = weekly_plan["days"][0]["meals"]["breakfast"]["selected_foods"]
    assert len(day1_bf) > 0
    target_food = day1_bf[0]["food_name"]

    replace_payload = {
        "weekly_plan": weekly_plan,
        "day": 1,
        "meal_type": "breakfast",
        "target_food_name": target_food,
        "dietary_preference": "vegetarian",
        "allergies_intolerances": ["gluten"]
    }

    resp = client.post("/api/v1/meal-plans/replace", json=replace_payload, headers=AUTH_HEADER)
    assert resp.status_code == 200, resp.text
    rep_data = resp.json()

    assert "original_food" in rep_data
    assert "replacement_food" in rep_data
    assert "updated_weekly_plan" in rep_data
    assert rep_data["original_food"]["food_name"] == target_food

def test_unauthenticated_replacement_request_rejected():
    replace_payload = {
        "weekly_plan": {"days": [], "deficiency_class": "Healthy", "medical_disclaimer": "test"},
        "day": 1,
        "meal_type": "breakfast",
        "target_food_name": "Apple"
    }
    response = client.post("/api/v1/meal-plans/replace", json=replace_payload)
    assert response.status_code in {401, 403}

def test_replacement_validation_for_nonexistent_item():
    gen_resp = client.post("/api/v1/meal-plans/generate", json=GENERATE_PAYLOAD, headers=AUTH_HEADER)
    weekly_plan = gen_resp.json()

    replace_payload = {
        "weekly_plan": weekly_plan,
        "day": 1,
        "meal_type": "breakfast",
        "target_food_name": "NonExistentItemXYZ123"
    }

    resp = client.post("/api/v1/meal-plans/replace", json=replace_payload, headers=AUTH_HEADER)
    assert resp.status_code == 400
    assert "not found" in resp.json()["detail"].lower()
