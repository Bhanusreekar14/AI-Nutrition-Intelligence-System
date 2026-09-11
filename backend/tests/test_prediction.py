import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# Dummy valid JWT token for auth header (development mock mode)
AUTH_HEADER = {
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIwMDAwMDAwMC0wMDAwLTAwMDAtMDAwMC0wMDAwMDAwMDAwMDEiLCJlbWFpbCI6InVzZXJAZXhhbXBsZS5jb20iLCJyb2xlIjoiYXV0aGVudGljYXRlZCJ9.dummy_signature"
}

VALID_PAYLOAD = {
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

def test_predict_deficiency_risk_valid():
    response = client.post("/api/v1/predict", json=VALID_PAYLOAD, headers=AUTH_HEADER)
    assert response.status_code == 200, response.text
    data = response.json()

    # Check root fields
    assert "predicted_class" in data
    assert "predicted_probability" in data
    assert "risk_score" in data
    assert "risk_level" in data
    assert "class_probabilities" in data
    assert "explanation" in data
    assert "medical_disclaimer" in data

    # Check predicted_class
    valid_classes = {"Anemia", "Healthy", "Night_Blindness", "Rickets_Osteomalacia", "Scurvy"}
    assert data["predicted_class"] in valid_classes

    # Check predicted_probability range
    prob = data["predicted_probability"]
    assert 0.0 <= prob <= 1.0

    # Check class_probabilities
    class_probs = data["class_probabilities"]
    assert len(class_probs) == 5
    assert sum(class_probs.values()) == pytest.approx(1.0, abs=0.01)

    # Check risk_score and risk_level
    score = data["risk_score"]
    assert 0.0 <= score <= 100.0
    valid_levels = {"Low Risk", "Moderate Risk", "High Risk", "Very High Risk"}
    assert data["risk_level"] in valid_levels

    # Check SHAP explanation
    exp = data["explanation"]
    assert "top_positive_features" in exp
    assert "top_negative_features" in exp
    assert isinstance(exp["top_positive_features"], list)
    assert isinstance(exp["top_negative_features"], list)

    # Check disclaimer
    assert "medical" in data["medical_disclaimer"].lower()

def test_predict_deficiency_risk_missing_required_field():
    invalid_payload = VALID_PAYLOAD.copy()
    del invalid_payload["age"]
    response = client.post("/api/v1/predict", json=invalid_payload, headers=AUTH_HEADER)
    assert response.status_code == 422

def test_predict_deficiency_risk_invalid_numerical_value():
    invalid_payload = VALID_PAYLOAD.copy()
    invalid_payload["age"] = -5.0  # Invalid age <= 0
    response = client.post("/api/v1/predict", json=invalid_payload, headers=AUTH_HEADER)
    assert response.status_code == 422
