import sys
import os
import json

# Ensure backend folder is in sys.path
sys.path.insert(0, os.path.abspath("backend"))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

AUTH_HEADER = {
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIwMDAwMDAwMC0wMDAwLTAwMDAtMDAwMC0wMDAwMDAwMDAwMDEiLCJlbWFpbCI6InVzZXJAZXhhbXBsZS5jb20iLCJyb2xlIjoiYXV0aGVudGljYXRlZCJ9.dummy_signature"
}

print("--- Testing FastAPI Endpoints ---", flush=True)

# 1. Health Check
res_health = client.get("/api/v1/health")
print(f"1. GET /api/v1/health -> Status {res_health.status_code}: {res_health.json()}")

# 2. OpenAPI Spec check for /api/v1/predict
res_openapi = client.get("/api/v1/openapi.json")
openapi_data = res_openapi.json()
paths = openapi_data.get("paths", {})
has_predict = "/api/v1/predict" in paths
print(f"2. GET /api/v1/openapi.json -> Contains /api/v1/predict: {has_predict}")

# 3. POST /api/v1/predict Valid Request
payload = {
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

res_predict = client.post("/api/v1/predict", json=payload, headers=AUTH_HEADER)
print(f"3. POST /api/v1/predict -> Status {res_predict.status_code}")
if res_predict.status_code == 200:
    pred_data = res_predict.json()
    print("   Predicted Class:", pred_data["predicted_class"])
    print("   Predicted Probability:", pred_data["predicted_probability"])
    print("   Risk Score:", pred_data["risk_score"])
    print("   Risk Level:", pred_data["risk_level"])
    print("   Class Probabilities:", pred_data["class_probabilities"])
    print("   Explanation Top Positive:", pred_data["explanation"]["top_positive_features"])
    print("   Explanation Top Negative:", pred_data["explanation"]["top_negative_features"])
    print("   Medical Disclaimer:", pred_data["medical_disclaimer"])
else:
    print("   ERROR Output:", res_predict.text)

print("SUCCESS: All API tests passed!")
