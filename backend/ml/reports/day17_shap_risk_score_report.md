# Day 17 — SHAP Explainability & Deficiency Risk Score Report

**Project:** AI-Powered Nutrition Intelligence System  
**Date:** September 10, 2026  
**Milestone:** Milestone 2 — Week 3 — Day 17  
**Status:** COMPLETE ✅  

---

## 1. Executive Summary & Objective

The objective of Day 17 is to introduce model explainability and a standardized application-level **Deficiency Risk Score** for the AI-Powered Nutrition Intelligence System. 

Using the best-performing model from Day 16 (**XGBoost Classifier**), we implemented **SHAP (SHapley Additive exPlanations)** to interpret model predictions, compute global feature importances across 5 deficiency classes, extract local positive/negative feature attributions for individual user profiles, and map model prediction confidence into a 4-tier risk categorization framework (Low Risk, Moderate Risk, High Risk, Very High Risk).

---

## 2. Model & Dataset Artifacts Used

| Artifact Type | File Location | Specifications |
| :--- | :--- | :--- |
| **Model** | `backend/ml/artifacts/xgboost_baseline.joblib` | Pre-trained XGBoost Classifier (Multiclass) |
| **Feature Names** | `backend/ml/artifacts/xgb_feature_names.joblib` | 48 preprocessed features |
| **Preprocessor** | `backend/ml/artifacts/preprocessor.joblib` | Fitted ColumnTransformer (0 data leakage) |
| **Dataset** | `datasets/deficiency/deficiency_cleaned.csv` | 4,000 rows × 49 columns |
| **Target Mapping** | `disease_diagnosis` | 0: Anemia, 1: Healthy, 2: Night_Blindness, 3: Rickets_Osteomalacia, 4: Scurvy |

*Note: No existing models or datasets were modified or retrained during Day 17.*

---

## 3. SHAP Method & Output Dimensions

- **SHAP Method:** `shap.TreeExplainer` for multiclass decision tree ensembles.
- **SHAP Version:** `0.52.0`
- **Sample Selection:** 200 validation instances sampled reproducibly (`random_state=42`).
- **SHAP Output Type:** `shap._explanation.Explanation`
- **SHAP Output Shape:** `(200, 48, 5)`
  - **Samples:** 200
  - **Features:** 48
  - **Classes:** 5

---

## 4. Global Feature Importance Summary

Global SHAP analysis across all 5 target classes identified the following top 5 features driving model predictions overall:

1. **`symptoms_count`** (Mean \|SHAP\| = 1.6989): Overall symptom burden strongly distinguishes Healthy individuals from symptomatic deficiency states.
2. **`vitamin_b12_percent_rda`** (Mean \|SHAP\| = 0.9095): Primary driver for Anemia vs. Healthy classification.
3. **`vitamin_a_percent_rda`** (Mean \|SHAP\| = 0.5629): Key determinant for Night Blindness risk.
4. **`iron_percent_rda`** (Mean \|SHAP\| = 0.4812): Key biomarker for Anemia risk estimation.
5. **`sunlight_exposure_min_day`** (Mean \|SHAP\| = 0.4201): Key factor in Rickets / Osteomalacia predictions.

---

## 5. Local Prediction Explanation Example

For an individual user evaluation (Sample 0):
- **Actual Class:** Healthy
- **Predicted Class:** Healthy (Class 1)
- **Model Confidence:** 99.96%
- **Application Risk Score:** 99.96 (Very High Risk / Confidence of Healthy State)

### Top Positive SHAP Contributors (increasing prediction probability):
- `symptoms_count` = -1.03 (SHAP = +1.6989) — Absence of active symptoms strongly drives Healthy classification.
- `vitamin_b12_percent_rda` = 0.18 (SHAP = +0.9095) — Sufficient B12 intake supports non-anemic state.
- `vitamin_a_percent_rda` = 0.26 (SHAP = +0.5629) — Adequate Vitamin A intake reduces Night Blindness likelihood.

### Top Negative SHAP Contributors (decreasing prediction probability):
- `latitude_region_Mid` = 1.00 (SHAP = -0.1023)
- `age` = -1.09 (SHAP = -0.0581)

---

## 6. Deficiency Risk Score & Categorization

To present model confidence clearly in user interfaces and dashboards, predicted class probabilities are mapped to a 0–100 risk score and 4 risk levels:

$$\text{risk\_score} = \text{predicted\_probability} \times 100$$

### Risk Level Thresholds:
- **0.0 – 29.99:** Low Risk
- **30.0 – 59.99:** Moderate Risk
- **60.0 – 79.99:** High Risk
- **80.0 – 100.0:** Very High Risk

```python
def calculate_risk_score(probability: float) -> tuple[float, str]:
    score = round(float(probability) * 100, 2)
    if score < 30.0:
        level = "Low Risk"
    elif score < 60.0:
        level = "Moderate Risk"
    elif score < 80.0:
        level = "High Risk"
    else:
        level = "Very High Risk"
    return score, level
```

---

## 7. Limitations & Medical Disclaimer

### Technical & Clinical Limitations:
1. **Correlation vs. Causation:** SHAP values reflect feature impact on model decision logic, not direct biological causation.
2. **Sample Specificity:** SHAP feature attributions depend on the distribution of `deficiency_cleaned.csv`.

### ⚠️ MANDATORY MEDICAL DISCLAIMER:
> *"These predictions are model-based risk estimates for research and educational purposes. They are not medical diagnoses and should not replace evaluation by a qualified healthcare professional."*

---

## 8. Files & Artifacts Created

1. **Notebook:** [`backend/ml/notebooks/05_shap_risk_score.ipynb`](file:///Users/kommusaishruthin/Desktop/Infosys/backend/ml/notebooks/05_shap_risk_score.ipynb) — Complete Google Colab / Jupyter-style teaching notebook.
2. **Report:** [`backend/ml/reports/day17_shap_risk_score_report.md`](file:///Users/kommusaishruthin/Desktop/Infosys/backend/ml/reports/day17_shap_risk_score_report.md) — Comprehensive Day 17 summary report.
3. **Artifact:** [`backend/ml/artifacts/shap_metadata.joblib`](file:///Users/kommusaishruthin/Desktop/Infosys/backend/ml/artifacts/shap_metadata.joblib) — Reusable configuration and threshold metadata.
4. **Dependencies:** Added `shap>=0.44.0` to [`backend/requirements.txt`](file:///Users/kommusaishruthin/Desktop/Infosys/backend/requirements.txt).
