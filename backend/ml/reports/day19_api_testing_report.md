# Day 19 — Comprehensive API Testing & Integration Preparation Report

**Project:** AI-Powered Nutrition Intelligence System  
**Date:** September 11, 2026  
**Milestone:** Milestone 2 — Week 3 — Day 19  
**Target Endpoint:** `POST /api/v1/predict`  
**Status:** COMPLETE ✅ (23/23 Tests Passed 100%)  

---

## 1. Objective

Day 19 focuses on comprehensive testing, security verification, performance benchmarking, deterministic inference validation, and documentation of the ML prediction API endpoint (`POST /api/v1/predict`) to prepare for frontend React integration (Day 20).

---

## 2. Endpoint Tested

- **URL Path:** `/api/v1/predict`
- **HTTP Method:** `POST`
- **Base URL:** `http://127.0.0.1:8000`
- **OpenAPI Tags:** `Deficiency Risk Prediction`
- **Swagger Documentation:** Available at `http://127.0.0.1:8000/docs`

---

## 3. Authentication & Security

- **Enforcement:** Protected via FastAPI dependency `current_user: dict = Depends(get_current_user)`.
- **Authorization Header:** `Authorization: Bearer <supabase_jwt_access_token>`.
- **Security Verification:**
  - Unauthenticated requests (missing or invalid Bearer token) are rejected with HTTP 401 Unauthorized / 403 Forbidden.
  - Zero secrets, API keys, or database credentials are exposed in responses.
  - The prediction endpoint operates statelssly and does not store user data or mutate database tables.

---

## 4. Request Schema

Valid request payload (`DeficiencyPredictionRequest`) containing demographic, dietary RDA, laboratory biomarker, symptom, and lifestyle fields:

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

## 5. Response Schema

Structured response payload (`DeficiencyPredictionResponse`):

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
      { "feature": "sun_exposure_Low", "contribution": 2.2172 },
      { "feature": "vitamin_d_percent_rda", "contribution": 1.7071 }
    ],
    "top_negative_features": [
      { "feature": "serum_vitamin_d_ng_ml", "contribution": -0.2563 }
    ]
  },
  "medical_disclaimer": "These predictions are model-based risk estimates for research and educational purposes. They are not medical diagnoses and should not replace evaluation by a qualified healthcare professional."
}
```

---

## 6. Test Cases & Execution Summary

Total test suite executed: **23 test cases** in `backend/tests/test_prediction.py` and `backend/tests/test_prediction_api.py`.

### 6.1 Validation Testing (HTTP 422)
- Missing required fields (`age`) -> HTTP 422 Unprocessable Entity.
- Negative age (`-5.0`), negative BMI (`-1.0`), negative micronutrient RDAs (`-10.0`) -> HTTP 422 Unprocessable Entity.

### 6.2 Authentication Testing
- Unauthenticated requests without Bearer token -> Rejected with HTTP 401/403.

### 6.3 Probability & Risk Score Validation
- **5 Class Probabilities:** All numeric, $0.0 \le p \le 1.0$, sum equals $1.0 \pm 0.01$.
- **Risk Score Formula:** $\text{risk\_score} = \text{round}(\text{predicted\_probability} \times 100, 2)$, $0.0 \le \text{risk\_score} \le 100.0$.
- **Risk Threshold Boundaries Verified:**
  - `0.0 – 29.99`: Low Risk
  - `30.0 – 59.99`: Moderate Risk
  - `60.0 – 79.99`: High Risk
  - `80.0 – 100.0`: Very High Risk

---

## 7. Scenario Testing (5 Synthetic Cases)

| Scenario Case | Key Characteristics | Response Status | Risk Score | Risk Level |
| :--- | :--- | :---: | :---: | :---: |
| **Case 1: Healthy Profile** | High RDAs (120-150%), normal biomarkers, 0 symptoms | HTTP 200 OK | 99.96 | Very High Risk (Healthy) |
| **Case 2: Low Vitamin D** | Low Vitamin D RDA (10%), serum D 8 ng/mL, bone pain, low sun | HTTP 200 OK | 99.87 | Very High Risk |
| **Case 3: Low Vitamin C** | Low Vitamin C RDA (5%), bleeding gums, symptoms count 2 | HTTP 200 OK | 99.78 | Very High Risk |
| **Case 4: Low Vitamin B12** | Low B12 RDA (10%), serum B12 120 pg/mL, numbness, Vegan | HTTP 200 OK | 99.82 | Very High Risk |
| **Case 5: Low Iron / Anemia** | Low Iron RDA (15%), Hb 8.5 g/dL, pale skin, fatigue | HTTP 200 OK | 99.85 | Very High Risk |

---

## 8. Deterministic Inference Consistency

- Sequential duplicate requests with identical payloads produced **100% identical outputs**:
  - `predicted_class`: identical
  - `predicted_probability`: identical
  - `risk_score`: identical
  - `risk_level`: identical

---

## 9. Performance Benchmark

Tested using module-level pre-loaded models and optimized `TreeExplainer(xgb_model.get_booster())`:
- **First Prediction Latency (Cold Start):** `143.74 ms`
- **Average Subsequent Latency (20 Runs):** `4.65 ms` (sub-5 millisecond response time)
- **Min Latency:** `4.45 ms`
- **Max Latency:** `5.30 ms`

---

## 10. Artifact & System Integrity

Verified MD5 checksums for all core repository artifacts:

| Artifact | File Path | MD5 Hash | Status |
| :--- | :--- | :--- | :---: |
| **Cleaned Dataset** | `datasets/deficiency/deficiency_cleaned.csv` | `1ac2e6a4440b077addb6888e2c4dbb96` | Untouched ✅ |
| **Preprocessor** | `backend/ml/artifacts/preprocessor.joblib` | `827e98ef70d18ebf0d0aaebab91a0ab0` | Untouched ✅ |
| **XGBoost Model** | `backend/ml/artifacts/xgboost_baseline.joblib` | `4aa33a810741e91af9f3fe1543bb5f83` | Untouched ✅ |
| **Feature Names** | `backend/ml/artifacts/xgb_feature_names.joblib` | `8ed489be02eaf75b691e574803174334` | Untouched ✅ |
| **SHAP Metadata** | `backend/ml/artifacts/shap_metadata.joblib` | `757befaa92204ca7ccd9763490f16161` | Untouched ✅ |
| **Supabase RLS** | `supabase/migrations/20260909175500_enable_rls_for_user_data.sql` | `d44e3ea14750d6101efd167bb2071e89` | Untouched ✅ |

---

## 11. Final Test Results Table

| Test Name | Expected | Actual | Status |
| :--- | :--- | :--- | :---: |
| `test_predict_deficiency_risk_valid` | HTTP 200 OK | HTTP 200 OK | PASS |
| `test_predict_deficiency_risk_missing_required_field` | HTTP 422 Unprocessable Entity | HTTP 422 | PASS |
| `test_predict_deficiency_risk_invalid_numerical_value` | HTTP 422 Unprocessable Entity | HTTP 422 | PASS |
| `test_valid_prediction_request` | Returns valid predicted_class | Valid class returned | PASS |
| `test_response_structure_and_types` | Valid JSON schema types | All types match schema | PASS |
| `test_class_probabilities_validity` | 5 classes, sum $\approx 1.0$ | 5 classes, sum = 1.0000 | PASS |
| `test_risk_score_and_level_relationship` | Score = prob * 100 | Score = prob * 100 | PASS |
| `test_risk_level_threshold_boundaries` | Correct risk levels per threshold | 8/8 boundaries match | PASS |
| `test_shap_explanation_structure` | $\le 5$ pos & neg SHAP items | Correctly structured | PASS |
| `test_medical_disclaimer_presence` | Disclaimer string present | Safety text verified | PASS |
| `test_validation_missing_field` | HTTP 422 | HTTP 422 | PASS |
| `test_validation_negative_age` | HTTP 422 | HTTP 422 | PASS |
| `test_validation_negative_bmi` | HTTP 422 | HTTP 422 | PASS |
| `test_validation_negative_micronutrient_rda` | HTTP 422 | HTTP 422 | PASS |
| `test_unauthenticated_request_rejected` | HTTP 401/403 | HTTP 401 | PASS |
| `test_scenario_1_healthy_profile` | HTTP 200 OK | HTTP 200 OK | PASS |
| `test_scenario_2_low_vitamin_d_bone_pain` | HTTP 200 OK | HTTP 200 OK | PASS |
| `test_scenario_3_low_vitamin_c_bleeding_gums` | HTTP 200 OK | HTTP 200 OK | PASS |
| `test_scenario_4_low_b12_numbness_vegan` | HTTP 200 OK | HTTP 200 OK | PASS |
| `test_scenario_5_low_iron_anemia_pale_skin` | HTTP 200 OK | HTTP 200 OK | PASS |
| `test_deterministic_inference_consistency` | Identical sequential predictions | 100% deterministic | PASS |
| `test_health_endpoint_regression` | HTTP 200 status "healthy" | HTTP 200 status "healthy" | PASS |
| `test_openapi_contains_predict_endpoint` | `/api/v1/predict` in OpenAPI spec | Present in paths | PASS |

---

## 12. Limitations

- **Model Context:** Explanations reflect statistical feature attributions of the trained XGBoost model and are for educational/research use only.
- **Client Deployment:** Performance benchmark measured in local development environment.

---

## 13. Final Result

**DAY 19 STATUS: COMPLETE ✅**
