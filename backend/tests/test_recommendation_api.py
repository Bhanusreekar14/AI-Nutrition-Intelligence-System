import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# Dummy auth header matching dev test pattern
AUTH_HEADER = {
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIwMDAwMDAwMC0wMDAwLTAwMDAtMDAwMC0wMDAwMDAwMDAwMDEiLCJlbWFpbCI6InVzZXJAZXhhbXBsZS5jb20iLCJyb2xlIjoiYXV0aGVudGljYXRlZCJ9.Dx9cvnLGMzsbCfrQ3jZzepEjsepkrsOiZVPlCUpSIuQ"
}

VALID_PAYLOAD = {
    "predicted_class": "Anemia",
    "risk_level": "High Risk",
    "risk_score": 75.0,
    "dietary_preference": "omnivore",
    "allergies_intolerances": [],
    "limit": 5
}

def test_authenticated_valid_recommendation_request():
    response = client.post("/api/v1/recommendations", json=VALID_PAYLOAD, headers=AUTH_HEADER)
    assert response.status_code == 200, response.text

def test_unauthenticated_recommendation_request_rejected():
    response = client.post("/api/v1/recommendations", json=VALID_PAYLOAD)
    assert response.status_code in {401, 403}

def test_recommendation_response_structure_and_keys():
    response = client.post("/api/v1/recommendations", json=VALID_PAYLOAD, headers=AUTH_HEADER)
    assert response.status_code == 200
    data = response.json()

    assert "predicted_class" in data
    assert "risk_level" in data
    assert "risk_score" in data
    assert "targeted_nutrients" in data
    assert "recommended_foods" in data
    assert "dietary_advice" in data
    assert "medical_disclaimer" in data

    assert isinstance(data["targeted_nutrients"], list)
    assert isinstance(data["recommended_foods"], list)
    assert isinstance(data["dietary_advice"], list)
    assert isinstance(data["medical_disclaimer"], str)

def test_recommended_food_objects_contain_valid_information():
    response = client.post("/api/v1/recommendations", json=VALID_PAYLOAD, headers=AUTH_HEADER)
    data = response.json()
    foods = data["recommended_foods"]
    assert len(foods) > 0
    for food in foods:
        assert "food_name" in food and food["food_name"]
        assert "ranking_score" in food and isinstance(food["ranking_score"], (int, float))
        assert "recommendation_reason" in food and food["recommendation_reason"]

def test_recommendation_limit_is_respected():
    payload = VALID_PAYLOAD.copy()
    payload["limit"] = 3
    response = client.post("/api/v1/recommendations", json=payload, headers=AUTH_HEADER)
    assert response.status_code == 200
    data = response.json()
    assert len(data["recommended_foods"]) <= 3

def test_anemia_request_returns_iron_focused_recommendations():
    payload = VALID_PAYLOAD.copy()
    payload["predicted_class"] = "Anemia"
    response = client.post("/api/v1/recommendations", json=payload, headers=AUTH_HEADER)
    assert response.status_code == 200
    data = response.json()
    assert data["predicted_class"] == "Anemia"
    assert "iron_mg" in data["targeted_nutrients"]
    for food in data["recommended_foods"]:
        assert "iron" in food["recommendation_reason"].lower()

def test_scurvy_request_returns_vitamin_c_focused_recommendations():
    payload = VALID_PAYLOAD.copy()
    payload["predicted_class"] = "Scurvy"
    response = client.post("/api/v1/recommendations", json=payload, headers=AUTH_HEADER)
    assert response.status_code == 200
    data = response.json()
    assert data["predicted_class"] == "Scurvy"
    assert "vitamin_c_mg" in data["targeted_nutrients"]
    for food in data["recommended_foods"]:
        assert "vitamin c" in food["recommendation_reason"].lower()

def test_rickets_osteomalacia_request_returns_calcium_focused_recommendations():
    payload = VALID_PAYLOAD.copy()
    payload["predicted_class"] = "Rickets_Osteomalacia"
    response = client.post("/api/v1/recommendations", json=payload, headers=AUTH_HEADER)
    assert response.status_code == 200
    data = response.json()
    assert data["predicted_class"] == "Rickets_Osteomalacia"
    assert "calcium_mg" in data["targeted_nutrients"]
    for food in data["recommended_foods"]:
        assert "calcium" in food["recommendation_reason"].lower()

def test_night_blindness_uses_rule_based_food_signal():
    payload = VALID_PAYLOAD.copy()
    payload["predicted_class"] = "Night_Blindness"
    response = client.post("/api/v1/recommendations", json=payload, headers=AUTH_HEADER)
    assert response.status_code == 200
    data = response.json()
    assert data["predicted_class"] == "Night_Blindness"
    assert "vitamin_a_rule_signal" in data["targeted_nutrients"]

def test_vegetarian_filtering_works_via_api():
    payload = VALID_PAYLOAD.copy()
    payload["dietary_preference"] = "vegetarian"
    response = client.post("/api/v1/recommendations", json=payload, headers=AUTH_HEADER)
    assert response.status_code == 200
    data = response.json()
    non_veg_terms = ["beef", "pork", "chicken", "turkey", "lamb", "tuna", "salmon", "shrimp"]
    for food in data["recommended_foods"]:
        name_lower = food["food_name"].lower()
        for term in non_veg_terms:
            assert term not in name_lower

def test_vegan_filtering_works_via_api():
    payload = VALID_PAYLOAD.copy()
    payload["dietary_preference"] = "vegan"
    response = client.post("/api/v1/recommendations", json=payload, headers=AUTH_HEADER)
    assert response.status_code == 200
    data = response.json()
    animal_terms = ["milk", "cheese", "butter", "yogurt", "cream", "egg", "beef", "chicken", "fish"]
    for food in data["recommended_foods"]:
        name_lower = food["food_name"].lower()
        for term in animal_terms:
            assert term not in name_lower

def test_allergy_filtering_works_via_api():
    payload = VALID_PAYLOAD.copy()
    payload["allergies_intolerances"] = ["dairy", "nuts"]
    response = client.post("/api/v1/recommendations", json=payload, headers=AUTH_HEADER)
    assert response.status_code == 200
    data = response.json()
    dairy_nut_terms = ["milk", "cheese", "butter", "cream", "yogurt", "peanut", "almond", "cashew", "walnut"]
    for food in data["recommended_foods"]:
        name_lower = food["food_name"].lower()
        for term in dairy_nut_terms:
            assert term not in name_lower

def test_invalid_deficiency_class_handled_safely():
    payload = VALID_PAYLOAD.copy()
    payload["predicted_class"] = "NonExistentDiagnosis"
    response = client.post("/api/v1/recommendations", json=payload, headers=AUTH_HEADER)
    assert response.status_code == 200
    data = response.json()
    assert data["predicted_class"] == "Healthy"

def test_risk_score_within_valid_range():
    payload = VALID_PAYLOAD.copy()
    payload["risk_score"] = 92.5
    response = client.post("/api/v1/recommendations", json=payload, headers=AUTH_HEADER)
    assert response.status_code == 200
    data = response.json()
    assert 0.0 <= data["risk_score"] <= 100.0

def test_existing_prediction_endpoint_still_works():
    predict_payload = {
        "age": 35.0,
        "bmi": 22.5,
        "vitamin_a_percent_rda": 85.0,
        "vitamin_c_percent_rda": 90.0,
        "vitamin_d_percent_rda": 40.0,
        "vitamin_e_percent_rda": 75.0,
        "vitamin_b12_percent_rda": 60.0,
        "folate_percent_rda": 80.0,
        "calcium_percent_rda": 70.0,
        "iron_percent_rda": 50.0,
        "hemoglobin_g_dl": 11.5,
        "serum_vitamin_d_ng_ml": 18.0,
        "serum_vitamin_b12_pg_ml": 250.0,
        "serum_folate_ng_ml": 8.0,
        "symptoms_count": 2,
        "has_night_blindness": False,
        "has_fatigue": True,
        "has_bleeding_gums": False,
        "has_bone_pain": True,
        "has_muscle_weakness": False,
        "has_numbness_tingling": False,
        "has_memory_problems": False,
        "has_pale_skin": False,
        "gender": "Female",
        "smoking_status": "Never",
        "alcohol_consumption": "Moderate",
        "exercise_level": "Moderate",
        "diet_type": "Vegetarian",
        "sun_exposure": "Low",
        "income_level": "Middle",
        "latitude_region": "Mid"
    }
    response = client.post("/api/v1/predict", json=predict_payload, headers=AUTH_HEADER)
    assert response.status_code == 200
    data = response.json()
    assert "predicted_class" in data
    assert "risk_score" in data

def test_existing_health_endpoint_still_works():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
