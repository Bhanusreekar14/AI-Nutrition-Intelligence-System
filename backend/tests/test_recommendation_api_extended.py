import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

AUTH_HEADER = {
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIwMDAwMDAwMC0wMDAwLTAwMDAtMDAwMC0wMDAwMDAwMDAwMDEiLCJlbWFpbCI6InVzZXJAZXhhbXBsZS5jb20iLCJyb2xlIjoiYXV0aGVudGljYXRlZCJ9.Dx9cvnLGMzsbCfrQ3jZzepEjsepkrsOiZVPlCUpSIuQ"
}

BASE_PAYLOAD = {
    "predicted_class": "Anemia",
    "risk_level": "High Risk",
    "risk_score": 75.0,
    "dietary_preference": "omnivore",
    "allergies_intolerances": [],
    "limit": 5
}

# 1. Authenticated valid request
def test_ext_1_authenticated_valid_request():
    response = client.post("/api/v1/recommendations", json=BASE_PAYLOAD, headers=AUTH_HEADER)
    assert response.status_code == 200, response.text

# 2. Unauthenticated request
def test_ext_2_unauthenticated_request():
    response = client.post("/api/v1/recommendations", json=BASE_PAYLOAD)
    assert response.status_code in {401, 403}

# 3. Anemia recommendation
def test_ext_3_anemia_recommendation():
    payload = BASE_PAYLOAD.copy()
    payload["predicted_class"] = "Anemia"
    response = client.post("/api/v1/recommendations", json=payload, headers=AUTH_HEADER)
    assert response.status_code == 200
    data = response.json()
    assert data["predicted_class"] == "Anemia"
    assert "iron_mg" in data["targeted_nutrients"]

# 4. Scurvy recommendation
def test_ext_4_scurvy_recommendation():
    payload = BASE_PAYLOAD.copy()
    payload["predicted_class"] = "Scurvy"
    response = client.post("/api/v1/recommendations", json=payload, headers=AUTH_HEADER)
    assert response.status_code == 200
    data = response.json()
    assert data["predicted_class"] == "Scurvy"
    assert "vitamin_c_mg" in data["targeted_nutrients"]

# 5. Rickets_Osteomalacia recommendation
def test_ext_5_rickets_osteomalacia_recommendation():
    payload = BASE_PAYLOAD.copy()
    payload["predicted_class"] = "Rickets_Osteomalacia"
    response = client.post("/api/v1/recommendations", json=payload, headers=AUTH_HEADER)
    assert response.status_code == 200
    data = response.json()
    assert data["predicted_class"] == "Rickets_Osteomalacia"
    assert "calcium_mg" in data["targeted_nutrients"]

# 6. Night_Blindness recommendation
def test_ext_6_night_blindness_recommendation():
    payload = BASE_PAYLOAD.copy()
    payload["predicted_class"] = "Night_Blindness"
    response = client.post("/api/v1/recommendations", json=payload, headers=AUTH_HEADER)
    assert response.status_code == 200
    data = response.json()
    assert data["predicted_class"] == "Night_Blindness"
    assert "vitamin_a_rule_signal" in data["targeted_nutrients"]

# 7. Healthy recommendation
def test_ext_7_healthy_recommendation():
    payload = BASE_PAYLOAD.copy()
    payload["predicted_class"] = "Healthy"
    response = client.post("/api/v1/recommendations", json=payload, headers=AUTH_HEADER)
    assert response.status_code == 200
    data = response.json()
    assert data["predicted_class"] == "Healthy"

# 8. Vegetarian preference
def test_ext_8_vegetarian_preference():
    payload = BASE_PAYLOAD.copy()
    payload["dietary_preference"] = "vegetarian"
    response = client.post("/api/v1/recommendations", json=payload, headers=AUTH_HEADER)
    assert response.status_code == 200
    for food in response.json()["recommended_foods"]:
        name = food["food_name"].lower()
        for meat in ["chicken", "beef", "pork", "lamb", "tuna", "salmon"]:
            assert meat not in name

# 9. Vegan preference
def test_ext_9_vegan_preference():
    payload = BASE_PAYLOAD.copy()
    payload["dietary_preference"] = "vegan"
    response = client.post("/api/v1/recommendations", json=payload, headers=AUTH_HEADER)
    assert response.status_code == 200
    for food in response.json()["recommended_foods"]:
        name = food["food_name"].lower()
        for animal in ["milk", "cheese", "butter", "egg", "beef", "chicken"]:
            assert animal not in name

# 10. Keto preference
def test_ext_10_keto_preference():
    payload = BASE_PAYLOAD.copy()
    payload["dietary_preference"] = "keto"
    response = client.post("/api/v1/recommendations", json=payload, headers=AUTH_HEADER)
    assert response.status_code == 200
    for food in response.json()["recommended_foods"]:
        assert food["carbs_g"] <= 10.0

# 11. Paleo preference
def test_ext_11_paleo_preference():
    payload = BASE_PAYLOAD.copy()
    payload["dietary_preference"] = "paleo"
    response = client.post("/api/v1/recommendations", json=payload, headers=AUTH_HEADER)
    assert response.status_code == 200
    assert len(response.json()["recommended_foods"]) > 0

# 12. Allergy filtering
def test_ext_12_single_allergy_filtering():
    payload = BASE_PAYLOAD.copy()
    payload["allergies_intolerances"] = ["dairy"]
    response = client.post("/api/v1/recommendations", json=payload, headers=AUTH_HEADER)
    assert response.status_code == 200
    for food in response.json()["recommended_foods"]:
        name = food["food_name"].lower()
        for dairy in ["milk", "cheese", "butter", "cream", "yogurt"]:
            assert dairy not in name

# 13. Multiple allergies
def test_ext_13_multiple_allergies_filtering():
    payload = BASE_PAYLOAD.copy()
    payload["allergies_intolerances"] = ["dairy", "nuts", "gluten"]
    response = client.post("/api/v1/recommendations", json=payload, headers=AUTH_HEADER)
    assert response.status_code == 200
    for food in response.json()["recommended_foods"]:
        name = food["food_name"].lower()
        for term in ["milk", "cheese", "peanut", "almond", "wheat"]:
            assert term not in name

# 14. Recommendation limit
def test_ext_14_recommendation_limit():
    payload = BASE_PAYLOAD.copy()
    payload["limit"] = 4
    response = client.post("/api/v1/recommendations", json=payload, headers=AUTH_HEADER)
    assert response.status_code == 200
    assert len(response.json()["recommended_foods"]) <= 4

# 15. Invalid limit (le 0 or gt 50 -> HTTP 422 validation error)
def test_ext_15_invalid_limit():
    payload = BASE_PAYLOAD.copy()
    payload["limit"] = 0
    response = client.post("/api/v1/recommendations", json=payload, headers=AUTH_HEADER)
    assert response.status_code == 422

# 16. Invalid deficiency class
def test_ext_16_invalid_deficiency_class():
    payload = BASE_PAYLOAD.copy()
    payload["predicted_class"] = "InvalidClass999"
    response = client.post("/api/v1/recommendations", json=payload, headers=AUTH_HEADER)
    assert response.status_code == 200
    assert response.json()["predicted_class"] == "Healthy"

# 17. Risk score boundary values
def test_ext_17_risk_score_boundaries():
    for score in [0.0, 50.0, 100.0]:
        payload = BASE_PAYLOAD.copy()
        payload["risk_score"] = score
        response = client.post("/api/v1/recommendations", json=payload, headers=AUTH_HEADER)
        assert response.status_code == 200
        assert response.json()["risk_score"] == score

# 18. Empty or string allergy input
def test_ext_18_empty_or_string_allergy_input():
    payload = BASE_PAYLOAD.copy()
    payload["allergies_intolerances"] = "dairy, nuts"
    response = client.post("/api/v1/recommendations", json=payload, headers=AUTH_HEADER)
    assert response.status_code == 200

# 19. Response schema validation
def test_ext_19_response_schema_validation():
    response = client.post("/api/v1/recommendations", json=BASE_PAYLOAD, headers=AUTH_HEADER)
    data = response.json()
    expected_keys = {"predicted_class", "risk_level", "risk_score", "targeted_nutrients", "recommended_foods", "dietary_advice", "medical_disclaimer"}
    assert set(data.keys()) == expected_keys

# 20. Medical disclaimer
def test_ext_20_medical_disclaimer():
    response = client.post("/api/v1/recommendations", json=BASE_PAYLOAD, headers=AUTH_HEADER)
    data = response.json()
    assert "educational purposes" in data["medical_disclaimer"].lower()

# 21. Existing /api/v1/predict regression
def test_ext_21_predict_regression():
    predict_payload = {
        "age": 35.0, "bmi": 22.5, "vitamin_a_percent_rda": 85.0, "vitamin_c_percent_rda": 90.0,
        "vitamin_d_percent_rda": 40.0, "vitamin_e_percent_rda": 75.0, "vitamin_b12_percent_rda": 60.0,
        "folate_percent_rda": 80.0, "calcium_percent_rda": 70.0, "iron_percent_rda": 50.0,
        "hemoglobin_g_dl": 11.5, "serum_vitamin_d_ng_ml": 18.0, "serum_vitamin_b12_pg_ml": 250.0,
        "serum_folate_ng_ml": 8.0, "symptoms_count": 2, "has_night_blindness": False,
        "has_fatigue": True, "has_bleeding_gums": False, "has_bone_pain": True,
        "has_muscle_weakness": False, "has_numbness_tingling": False, "has_memory_problems": False,
        "has_pale_skin": False, "gender": "Female", "smoking_status": "Never",
        "alcohol_consumption": "Moderate", "exercise_level": "Moderate", "diet_type": "Vegetarian",
        "sun_exposure": "Low", "income_level": "Middle", "latitude_region": "Mid"
    }
    response = client.post("/api/v1/predict", json=predict_payload, headers=AUTH_HEADER)
    assert response.status_code == 200

# 22. Existing /api/v1/health regression
def test_ext_22_health_regression():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

# 23. Prohibited foods via API
def test_ext_23_prohibited_foods_via_api():
    payload = BASE_PAYLOAD.copy()
    payload["prohibited_foods"] = ["spinach", "liver"]
    response = client.post("/api/v1/recommendations", json=payload, headers=AUTH_HEADER)
    assert response.status_code == 200
    for food in response.json()["recommended_foods"]:
        name = food["food_name"].lower()
        assert "spinach" not in name
        assert "liver" not in name

# 24. Preferred foods via API
def test_ext_24_preferred_foods_via_api():
    payload = BASE_PAYLOAD.copy()
    payload["preferred_foods"] = "beans, lentils"
    response = client.post("/api/v1/recommendations", json=payload, headers=AUTH_HEADER)
    assert response.status_code == 200
    assert len(response.json()["recommended_foods"]) > 0
