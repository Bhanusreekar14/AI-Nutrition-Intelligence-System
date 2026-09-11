import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.deficiency_prediction_service import calculate_risk_score

client = TestClient(app)

# Dummy valid JWT token for auth header (development mock mode)
AUTH_HEADER = {
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIwMDAwMDAwMC0wMDAwLTAwMDAtMDAwMC0wMDAwMDAwMDAwMDEiLCJlbWFpbCI6InVzZXJAZXhhbXBsZS5jb20iLCJyb2xlIjoiYXV0aGVudGljYXRlZCJ9.dummy_signature"
}

BASE_PAYLOAD = {
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

# ============================================================================
# 1. VALID PREDICTION & RESPONSE STRUCTURE TESTS
# ============================================================================

def test_valid_prediction_request():
    response = client.post("/api/v1/predict", json=BASE_PAYLOAD, headers=AUTH_HEADER)
    assert response.status_code == 200, response.text
    data = response.json()
    assert "predicted_class" in data
    assert data["predicted_class"] in {"Anemia", "Healthy", "Night_Blindness", "Rickets_Osteomalacia", "Scurvy"}

def test_response_structure_and_types():
    response = client.post("/api/v1/predict", json=BASE_PAYLOAD, headers=AUTH_HEADER)
    assert response.status_code == 200
    data = response.json()

    assert isinstance(data["predicted_class"], str)
    assert isinstance(data["predicted_probability"], float)
    assert isinstance(data["risk_score"], float)
    assert isinstance(data["risk_level"], str)
    assert isinstance(data["class_probabilities"], dict)
    assert isinstance(data["explanation"], dict)
    assert isinstance(data["medical_disclaimer"], str)

def test_class_probabilities_validity():
    response = client.post("/api/v1/predict", json=BASE_PAYLOAD, headers=AUTH_HEADER)
    data = response.json()
    class_probs = data["class_probabilities"]

    assert len(class_probs) == 5
    expected_keys = {"Anemia", "Healthy", "Night_Blindness", "Rickets_Osteomalacia", "Scurvy"}
    assert set(class_probs.keys()) == expected_keys

    for cls, prob in class_probs.items():
        assert 0.0 <= prob <= 1.0, f"Probability for {cls} out of range: {prob}"

    total_prob = sum(class_probs.values())
    assert total_prob == pytest.approx(1.0, abs=0.01)

def test_risk_score_and_level_relationship():
    response = client.post("/api/v1/predict", json=BASE_PAYLOAD, headers=AUTH_HEADER)
    data = response.json()
    prob = data["predicted_probability"]
    score = data["risk_score"]
    level = data["risk_level"]

    assert 0.0 <= score <= 100.0
    assert score == pytest.approx(round(prob * 100, 2), abs=0.1)
    assert level in {"Low Risk", "Moderate Risk", "High Risk", "Very High Risk"}

# ============================================================================
# 2. RISK LEVEL BOUNDARY TESTS
# ============================================================================

def test_risk_level_threshold_boundaries():
    boundaries = [
        (0.0, 0.0, "Low Risk"),
        (0.2999, 29.99, "Low Risk"),
        (0.30, 30.0, "Moderate Risk"),
        (0.5999, 59.99, "Moderate Risk"),
        (0.60, 60.0, "High Risk"),
        (0.7999, 79.99, "High Risk"),
        (0.80, 80.0, "Very High Risk"),
        (1.0, 100.0, "Very High Risk"),
    ]
    for p, expected_score, expected_level in boundaries:
        score, level = calculate_risk_score(p)
        assert score == expected_score, f"Failed score for p={p}"
        assert level == expected_level, f"Failed level for p={p}"

# ============================================================================
# 3. SHAP EXPLANATION TESTS
# ============================================================================

def test_shap_explanation_structure():
    response = client.post("/api/v1/predict", json=BASE_PAYLOAD, headers=AUTH_HEADER)
    exp = response.json()["explanation"]

    assert "top_positive_features" in exp
    assert "top_negative_features" in exp

    pos_features = exp["top_positive_features"]
    neg_features = exp["top_negative_features"]

    assert len(pos_features) <= 5
    assert len(neg_features) <= 5

    for item in pos_features + neg_features:
        assert "feature" in item
        assert "contribution" in item
        assert isinstance(item["feature"], str)
        assert isinstance(item["contribution"], float)

def test_medical_disclaimer_presence():
    response = client.post("/api/v1/predict", json=BASE_PAYLOAD, headers=AUTH_HEADER)
    disclaimer = response.json()["medical_disclaimer"]
    assert "medical diagnoses" in disclaimer
    assert "research and educational purposes" in disclaimer

# ============================================================================
# 4. INPUT VALIDATION TESTS (HTTP 422)
# ============================================================================

def test_validation_missing_field():
    payload = BASE_PAYLOAD.copy()
    del payload["age"]
    response = client.post("/api/v1/predict", json=payload, headers=AUTH_HEADER)
    assert response.status_code == 422

def test_validation_negative_age():
    payload = BASE_PAYLOAD.copy()
    payload["age"] = -5.0
    response = client.post("/api/v1/predict", json=payload, headers=AUTH_HEADER)
    assert response.status_code == 422

def test_validation_negative_bmi():
    payload = BASE_PAYLOAD.copy()
    payload["bmi"] = -1.0
    response = client.post("/api/v1/predict", json=payload, headers=AUTH_HEADER)
    assert response.status_code == 422

def test_validation_negative_micronutrient_rda():
    payload = BASE_PAYLOAD.copy()
    payload["vitamin_c_percent_rda"] = -10.0
    response = client.post("/api/v1/predict", json=payload, headers=AUTH_HEADER)
    assert response.status_code == 422

# ============================================================================
# 5. AUTHENTICATION TEST
# ============================================================================

def test_unauthenticated_request_rejected():
    response = client.post("/api/v1/predict", json=BASE_PAYLOAD)
    assert response.status_code in {401, 403}

# ============================================================================
# 6. MULTIPLE NUTRITIONAL SCENARIOS
# ============================================================================

def test_scenario_1_healthy_profile():
    payload = BASE_PAYLOAD.copy()
    payload.update({
        "vitamin_a_percent_rda": 120.0,
        "vitamin_c_percent_rda": 150.0,
        "vitamin_d_percent_rda": 150.0,
        "vitamin_b12_percent_rda": 130.0,
        "iron_percent_rda": 120.0,
        "hemoglobin_g_dl": 14.5,
        "serum_vitamin_d_ng_ml": 40.0,
        "serum_vitamin_b12_pg_ml": 500.0,
        "symptoms_count": 0,
        "has_fatigue": False,
        "has_bone_pain": False,
        "sun_exposure": "High"
    })
    response = client.post("/api/v1/predict", json=payload, headers=AUTH_HEADER)
    assert response.status_code == 200
    data = response.json()
    assert data["predicted_class"] in {"Anemia", "Healthy", "Night_Blindness", "Rickets_Osteomalacia", "Scurvy"}

def test_scenario_2_low_vitamin_d_bone_pain():
    payload = BASE_PAYLOAD.copy()
    payload.update({
        "vitamin_d_percent_rda": 10.0,
        "serum_vitamin_d_ng_ml": 8.0,
        "has_bone_pain": True,
        "symptoms_count": 2,
        "sun_exposure": "Low"
    })
    response = client.post("/api/v1/predict", json=payload, headers=AUTH_HEADER)
    assert response.status_code == 200
    data = response.json()
    assert 0.0 <= data["risk_score"] <= 100.0

def test_scenario_3_low_vitamin_c_bleeding_gums():
    payload = BASE_PAYLOAD.copy()
    payload.update({
        "vitamin_c_percent_rda": 5.0,
        "has_bleeding_gums": True,
        "symptoms_count": 2
    })
    response = client.post("/api/v1/predict", json=payload, headers=AUTH_HEADER)
    assert response.status_code == 200
    data = response.json()
    assert data["predicted_class"] in {"Anemia", "Healthy", "Night_Blindness", "Rickets_Osteomalacia", "Scurvy"}

def test_scenario_4_low_b12_numbness_vegan():
    payload = BASE_PAYLOAD.copy()
    payload.update({
        "vitamin_b12_percent_rda": 10.0,
        "serum_vitamin_b12_pg_ml": 120.0,
        "has_numbness_tingling": True,
        "has_fatigue": True,
        "diet_type": "Vegan",
        "symptoms_count": 2
    })
    response = client.post("/api/v1/predict", json=payload, headers=AUTH_HEADER)
    assert response.status_code == 200
    data = response.json()
    assert data["predicted_class"] in {"Anemia", "Healthy", "Night_Blindness", "Rickets_Osteomalacia", "Scurvy"}

def test_scenario_5_low_iron_anemia_pale_skin():
    payload = BASE_PAYLOAD.copy()
    payload.update({
        "iron_percent_rda": 15.0,
        "hemoglobin_g_dl": 8.5,
        "has_pale_skin": True,
        "has_fatigue": True,
        "symptoms_count": 2
    })
    response = client.post("/api/v1/predict", json=payload, headers=AUTH_HEADER)
    assert response.status_code == 200
    data = response.json()
    assert data["predicted_class"] in {"Anemia", "Healthy", "Night_Blindness", "Rickets_Osteomalacia", "Scurvy"}

# ============================================================================
# 7. DETERMINISTIC CONSISTENCY TEST
# ============================================================================

def test_deterministic_inference_consistency():
    res1 = client.post("/api/v1/predict", json=BASE_PAYLOAD, headers=AUTH_HEADER).json()
    res2 = client.post("/api/v1/predict", json=BASE_PAYLOAD, headers=AUTH_HEADER).json()

    assert res1["predicted_class"] == res2["predicted_class"]
    assert res1["predicted_probability"] == res2["predicted_probability"]
    assert res1["risk_score"] == res2["risk_score"]
    assert res1["risk_level"] == res2["risk_level"]

# ============================================================================
# 8. OPENAPI & HEALTH REGRESSION TESTS
# ============================================================================

def test_health_endpoint_regression():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_openapi_contains_predict_endpoint():
    response = client.get("/api/v1/openapi.json")
    assert response.status_code == 200
    openapi = response.json()
    assert "/api/v1/predict" in openapi.get("paths", {})
