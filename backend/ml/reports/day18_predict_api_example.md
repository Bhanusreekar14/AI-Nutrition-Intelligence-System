# Day 18 — ML Prediction API Endpoint Documentation & Test Guide

**Endpoint:** `POST /api/v1/predict`  
**Authentication:** Required (`Authorization: Bearer <supabase_jwt_token>`)  
**Content-Type:** `application/json`  

---

## 1. Overview

The `/api/v1/predict` endpoint exposes the trained **XGBoost Nutrition Deficiency ML Model** integrated with **SHAP feature explainability** and **application-level risk scoring**.

It accepts nutritional, demographic, biomarker, and symptom inputs, transforms them using the saved `preprocessor.joblib` pipeline (0 data leakage), computes prediction probabilities across 5 deficiency classes, assigns an application-level risk score (0–100) and risk level, extracts top SHAP feature attributions, and returns a structured JSON payload with a mandatory medical disclaimer.

---

## 2. Sample JSON Request

```json
{
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
  "has_night_blindness": false,
  "has_fatigue": true,
  "has_bleeding_gums": false,
  "has_bone_pain": true,
  "has_muscle_weakness": false,
  "has_numbness_tingling": false,
  "has_memory_problems": false,
  "has_pale_skin": false,
  "gender": "Female",
  "smoking_status": "Never",
  "alcohol_consumption": "Moderate",
  "exercise_level": "Moderate",
  "diet_type": "Vegetarian",
  "sun_exposure": "Low",
  "income_level": "Middle",
  "latitude_region": "Mid"
}
```

---

## 3. Sample JSON Response (HTTP 200 OK)

```json
{
  "predicted_class": "Rickets_Osteomalacia",
  "predicted_probability": 0.9987,
  "risk_score": 99.87,
  "risk_level": "Very High Risk",
  "class_probabilities": {
    "Anemia": 0.0004,
    "Healthy": 0.0008,
    "Night_Blindness": 0.0001,
    "Rickets_Osteomalacia": 0.9987,
    "Scurvy": 0.0001
  },
  "explanation": {
    "top_positive_features": [
      {
        "feature": "vitamin_d_percent_rda",
        "contribution": 1.4523
      },
      {
        "feature": "serum_vitamin_d_ng_ml",
        "contribution": 1.1205
      },
      {
        "feature": "has_bone_pain",
        "contribution": 0.8431
      },
      {
        "feature": "sun_exposure_Low",
        "contribution": 0.6521
      },
      {
        "feature": "symptoms_count",
        "contribution": 0.4120
      }
    ],
    "top_negative_features": [
      {
        "feature": "vitamin_c_percent_rda",
        "contribution": -0.1542
      },
      {
        "feature": "hemoglobin_g_dl",
        "contribution": -0.0912
      },
      {
        "feature": "gender_Female",
        "contribution": -0.0415
      }
    ]
  },
  "medical_disclaimer": "These predictions are model-based risk estimates for research and educational purposes. They are not medical diagnoses and should not replace evaluation by a qualified healthcare professional."
}
```

---

## 4. Example cURL Command

```bash
curl -X 'POST' \
  'http://localhost:8000/api/v1/predict' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer <YOUR_SUPABASE_JWT_ACCESS_TOKEN>' \
  -H 'Content-Type: application/json' \
  -d '{
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
  "has_night_blindness": false,
  "has_fatigue": true,
  "has_bleeding_gums": false,
  "has_bone_pain": true,
  "has_muscle_weakness": false,
  "has_numbness_tingling": false,
  "has_memory_problems": false,
  "has_pale_skin": false,
  "gender": "Female",
  "smoking_status": "Never",
  "alcohol_consumption": "Moderate",
  "exercise_level": "Moderate",
  "diet_type": "Vegetarian",
  "sun_exposure": "Low",
  "income_level": "Middle",
  "latitude_region": "Mid"
}'
```

---

## 5. OpenAPI & Interactive Docs Access

When the FastAPI server is running (`python3 backend/run_server.py`), interactive documentation is available at:
- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`
- **OpenAPI JSON Spec:** `http://localhost:8000/api/v1/openapi.json`
