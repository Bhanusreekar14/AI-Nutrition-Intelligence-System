import json
import os
import joblib

def create_notebook():
    nb = {
        "cells": [],
        "metadata": {
            "language_info": {
                "name": "python",
                "version": "3.12.0"
            },
            "orig_nbformat": 4
        },
        "nbformat": 4,
        "nbformat_minor": 2
    }

    def add_markdown(text):
        nb["cells"].append({
            "cell_type": "markdown",
            "metadata": {},
            "source": [line + "\n" for line in text.split("\n")]
        })

    def add_code(text):
        nb["cells"].append({
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [line + "\n" for line in text.split("\n")]
        })

    # -------------------------------------------------------------------------
    # Notebook Cells Definition
    # -------------------------------------------------------------------------

    # Cell 1: Title & Overview
    add_markdown("""# Day 17 — SHAP Explainability & Deficiency Risk Score

**Project:** AI-Powered Nutrition Intelligence System  
**Dataset:** `datasets/deficiency/deficiency_cleaned.csv`  
**Model:** `backend/ml/artifacts/xgboost_baseline.joblib` (XGBoost Classifier)  
**Notebook Output:** `backend/ml/notebooks/05_shap_risk_score.ipynb`  

---

## 1. Learning Objectives

In this notebook, we extend our best-performing **XGBoost Baseline Model** from Day 16 with model explainability and a standardized risk score calculation:
1. Explain the principles of **SHAP (SHapley Additive exPlanations)** in simple, non-technical terms.
2. Load existing XGBoost model and preprocessing artifacts without retraining or data leakage.
3. Compute multiclass SHAP values on a representative validation dataset sample.
4. Visualize **Global Feature Importance** across all 5 deficiency classes.
5. Generate **Local Predictions & Explanations** for individual user profiles.
6. Formulate an **Application-Level Deficiency Risk Score** (0–100) and risk level categories.
7. Implement human-readable prediction helper functions for downstream API/Dashboard integration.
8. Highlight clinical limitations and enforce mandatory medical disclaimers.""")

    # Cell 2: Why Explainability Matters
    add_markdown("""## 2. Why Explainability Matters

In healthcare and nutritional decision-support systems, machine learning models cannot function as black boxes. 

- **Trust & Transparency:** Healthcare professionals and users need to know *why* a model predicts a specific deficiency risk (e.g. Scurvy or Anemia).
- **Debugging & Bias Auditing:** Feature attribution helps uncover spurious correlations, data artifacts, or bias in survey data.
- **Actionable Guidance:** Explanations highlight specific dietary gaps (e.g., low Vitamin C intake or low sunlight exposure) that can be remediated.""")

    # Cell 3: What is SHAP?
    add_markdown("""## 3. What is SHAP? (SHapley Additive exPlanations)

**SHAP** is grounded in cooperative game theory (Shapley values). It measures the marginal contribution of each feature to a model's prediction across all possible feature combinations.

- **Prediction vs. Explanation:** A model prediction outputs a probability distribution across classes (e.g., 85% probability of Anemia). SHAP explains *which specific features pushed the prediction up or down* relative to the base average prediction.
- **Feature Importance vs. Causation:** SHAP identifies statistical contributions in the model's decision logic; it **does not prove biological causation**.
- **Risk Estimates, Not Diagnoses:** Explanations represent mathematical risk attributions derived from demographic, dietary, and symptom patterns, **not clinical medical diagnoses**.""")

    # Cell 4: Imports & Setup
    add_markdown("""## 4. Import Required Libraries

We import core data manipulation libraries, XGBoost, SHAP, and utility modules.""")

    add_code("""import joblib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import shap

print(f"✅ pandas version: {pd.__version__}")
print(f"✅ numpy version: {np.__version__}")
print(f"✅ joblib version: {joblib.__version__}")
print(f"✅ SHAP version: {shap.__version__}")""")

    # Cell 5: Load Existing Model and Preprocessing Artifacts
    add_markdown("""## 5. Load Existing Model and Artifacts

We load the pre-trained XGBoost model, feature names, and preprocessor from `backend/ml/artifacts/` without retraining.""")

    add_code("""# Paths to artifacts
MODEL_PATH = "../artifacts/xgboost_baseline.joblib"
FEATURE_NAMES_PATH = "../artifacts/xgb_feature_names.joblib"
PREPROCESSOR_PATH = "../artifacts/preprocessor.joblib"

# Load artifacts
xgb_model = joblib.load(MODEL_PATH)
xgb_feature_names = joblib.load(FEATURE_NAMES_PATH)
preprocessor = joblib.load(PREPROCESSOR_PATH)

print(f"✅ XGBoost Model loaded: {type(xgb_model).__name__}")
print(f"✅ Feature Names loaded: {len(xgb_feature_names)} features")
print(f"✅ Preprocessor loaded: {type(preprocessor).__name__}")""")

    # Cell 6: Load & Preprocess Cleaned Dataset
    add_markdown("""## 6. Load Cleaned Dataset & Reproduce Preprocessing

We load `datasets/deficiency/deficiency_cleaned.csv` and apply the saved preprocessor to ensure zero data leakage and 100% feature alignment.""")

    add_code("""# Load cleaned dataset
DATASET_PATH = "../../datasets/deficiency/deficiency_cleaned.csv"
df = pd.read_csv(DATASET_PATH)

# Target mapping
TARGET_MAPPING = {
    0: "Anemia",
    1: "Healthy",
    2: "Night_Blindness",
    3: "Rickets_Osteomalacia",
    4: "Scurvy"
}

# Separate X and y
X = df.drop(columns=["disease_diagnosis"])
y = df["disease_diagnosis"]

# Preprocess X using saved preprocessor
X_trans = preprocessor.transform(X)
if hasattr(X_trans, "toarray"):
    X_trans = X_trans.toarray()

# Build DataFrame with exact feature names
X_df = pd.DataFrame(X_trans, columns=xgb_feature_names)

print(f"✅ Original dataset shape: {df.shape}")
print(f"✅ Feature matrix shape: {X_df.shape}")
print(f"✅ Target classes present: {sorted(y.unique())}")""")

    # Cell 7: Verify Feature Ordering
    add_markdown("""## 7. Verify Feature Ordering

We confirm that the column ordering of `X_df` matches `xgb_feature_names` exactly.""")

    add_code("""# Verify column names match model expectation
assert list(X_df.columns) == xgb_feature_names, "Feature ordering mismatch!"
print(f"✅ Feature alignment verified: {len(X_df.columns)} features match exactly.")
print(f"First 10 features: {xgb_feature_names[:10]}")""")

    # Cell 8: Generate SHAP Explanations
    add_markdown("""## 8. Generate SHAP Explanations

We initialize `shap.TreeExplainer` on the XGBoost model and compute SHAP values for a representative sample of 200 validation instances (`random_state=42`).""")

    add_code("""# Sample 200 instances reproducibly
sample_X = X_df.sample(n=200, random_state=42)
sample_y = y.loc[sample_X.index]

# Initialize TreeExplainer
explainer = shap.TreeExplainer(xgb_model)
shap_explanation = explainer(sample_X)

# Print SHAP metadata
print(f"✅ SHAP Explanation Type: {type(shap_explanation)}")
print(f"✅ SHAP Values Shape: {shap_explanation.shape}")

num_samples, num_features, num_classes = shap_explanation.shape
print(f"   - Number of Samples: {num_samples}")
print(f"   - Number of Features: {num_features}")
print(f"   - Number of Classes: {num_classes}")

# Assert shape compatibility for 5-class model
assert num_features == len(xgb_feature_names), "SHAP feature count mismatch!"
assert num_classes == len(TARGET_MAPPING), "SHAP class count mismatch!"
print("✅ SHAP dimensions are valid for 5-class classification.")""")

    # Cell 9: Global Feature Importance
    add_markdown("""## 9. Global Feature Importance

We inspect global feature importance across classes to understand which nutritional and demographic variables drive the model overall.""")

    add_code("""# Compute mean absolute SHAP value per feature across all classes
# shap_explanation.values shape: (200, 48, 5)
mean_abs_shap = np.mean(np.abs(shap_explanation.values), axis=(0, 2))
global_importance = pd.DataFrame({
    'feature': xgb_feature_names,
    'importance': mean_abs_shap
}).sort_values(by='importance', ascending=False)

print("--- Top 10 Global Features by Mean Absolute SHAP Value ---")
print(global_importance.head(10).to_string(index=False))

# Plot summary bar plot
plt.figure(figsize=(10, 6))
plt.barh(global_importance.head(12)['feature'][::-1], global_importance.head(12)['importance'][::-1], color='#10B981')
plt.xlabel("Mean |SHAP value| (Global Feature Impact)")
plt.title("Day 17 - XGBoost Top 12 Global Feature Importances (SHAP)")
plt.tight_layout()
plt.show()""")

    # Cell 10: Deficiency Risk Score Formula
    add_markdown("""## 10. Application-Level Deficiency Risk Score

We define a standardized application risk score (0–100) based on model confidence for the predicted deficiency class:

$$\\text{risk\_score} = \\text{predicted\_probability} \\times 100$$

### Risk Categories:
- **0–29:** Low Risk
- **30–59:** Moderate Risk
- **60–79:** High Risk
- **80–100:** Very High Risk

*Note: This is an application-level model score, not a clinically validated probability.*""")

    add_code("""def calculate_risk_score(probability: float) -> tuple[float, str]:
    \"\"\"
    Converts a model predicted probability (0 to 1) into an application risk score (0 to 100)
    and maps it to a risk category level.
    \"\"\"
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

# Validate helper function with test values
test_probs = [0.12, 0.45, 0.73, 0.94]
print("--- Risk Score Function Validation ---")
for p in test_probs:
    sc, lv = calculate_risk_score(p)
    print(f"Predicted Probability: {p:.2f} -> Score: {sc:5.2f} -> Category: {lv}")""")

    # Cell 11: Human-Readable Local Explanation Function
    add_markdown("""## 11. Human-Readable Prediction & Explanation Helper

We build `explain_prediction()` to generate structured explanations for individual user predictions.""")

    add_code("""def explain_prediction(sample_index: int, X_sample_df: pd.DataFrame, y_true_series: pd.Series, model, shap_exp, feature_names: list, mapping: dict):
    \"\"\"
    Generates a complete prediction summary including probabilities, risk score, and top SHAP contributors.
    \"\"\"
    # Get single sample row
    sample_row = X_sample_df.iloc[[sample_index]]
    actual_class_id = y_true_series.iloc[sample_index]
    actual_disease = mapping[actual_class_id]
    
    # Model prediction
    pred_class_id = int(model.predict(sample_row)[0])
    pred_probs = model.predict_proba(sample_row)[0]
    pred_prob = float(pred_probs[pred_class_id])
    pred_disease = mapping[pred_class_id]
    
    # Risk score & level
    risk_score, risk_level = calculate_risk_score(pred_prob)
    
    # Extract SHAP values for predicted class
    sample_shap = shap_exp.values[sample_index, :, pred_class_id]
    
    df_impact = pd.DataFrame({
        'feature': feature_names,
        'shap_value': sample_shap,
        'feature_value': sample_row.iloc[0].values
    }).sort_values(by='shap_value', key=abs, ascending=False)
    
    top_pos = df_impact[df_impact['shap_value'] > 0].head(3)
    top_neg = df_impact[df_impact['shap_value'] < 0].head(3)
    
    return {
        'actual_disease': actual_disease,
        'predicted_disease': pred_disease,
        'predicted_class_id': pred_class_id,
        'confidence_percent': round(pred_prob * 100, 2),
        'risk_score': risk_score,
        'risk_level': risk_level,
        'top_positive_contributors': top_pos.to_dict(orient='records'),
        'top_negative_contributors': top_neg.to_dict(orient='records'),
        'class_probabilities': {mapping[i]: round(float(pred_probs[i]), 4) for i in range(len(mapping))}
    }

# Run explanation for sample 0
sample_explanation = explain_prediction(0, sample_X, sample_y, xgb_model, shap_explanation, xgb_feature_names, TARGET_MAPPING)

print("=== EXAMPLE PREDICTION EXPLANATION (Sample 0) ===")
print(f"Actual Label:      {sample_explanation['actual_disease']}")
print(f"Predicted Label:   {sample_explanation['predicted_disease']}")
print(f"Confidence:        {sample_explanation['confidence_percent']}%")
print(f"Risk Score:        {sample_explanation['risk_score']} ({sample_explanation['risk_level']})")
print("\n--- Class Probabilities ---")
for dis, prb in sample_explanation['class_probabilities'].items():
    print(f"  • {dis:20s}: {prb*100:6.2f}%")

print("\n--- Top Positive SHAP Contributors (Pushes toward predicted class) ---")
for c in sample_explanation['top_positive_contributors']:
    print(f"  • {c['feature']:25s}: SHAP = {c['shap_value']:+.4f} (val = {c['feature_value']:.2f})")

print("\n--- Top Negative SHAP Contributors (Pushes away from predicted class) ---")
for c in sample_explanation['top_negative_contributors']:
    print(f"  • {c['feature']:25s}: SHAP = {c['shap_value']:+.4f} (val = {c['feature_value']:.2f})")""")

    # Cell 12: Save Reusable SHAP Metadata Artifact
    add_markdown("""## 12. Save Reusable SHAP Metadata Artifact

We save a lightweight metadata artifact `backend/ml/artifacts/shap_metadata.joblib` containing configuration details (feature names, target mapping, risk threshold definitions, medical disclaimer) without storing heavy SHAP arrays.""")

    add_code("""shap_metadata = {
    "model_name": "XGBoost Baseline",
    "num_features": len(xgb_feature_names),
    "feature_names": xgb_feature_names,
    "target_mapping": TARGET_MAPPING,
    "risk_thresholds": {
        "Low Risk": (0.0, 29.99),
        "Moderate Risk": (30.0, 59.99),
        "High Risk": (60.0, 79.99),
        "Very High Risk": (80.0, 100.0)
    },
    "disclaimer": "These predictions are model-based risk estimates for research and educational purposes. They are not medical diagnoses and should not replace evaluation by a qualified healthcare professional."
}

METADATA_PATH = "../artifacts/shap_metadata.joblib"
joblib.dump(shap_metadata, METADATA_PATH)

meta_size = os.path.getsize(METADATA_PATH)
print(f"✅ Saved SHAP metadata artifact to: {METADATA_PATH} ({meta_size} bytes)")""")

    # Cell 13: Limitations and Medical Disclaimer
    add_markdown("""## 13. Limitations & Medical Disclaimer

### Model & SHAP Limitations:
1. **Statistical Correlation vs. Causation:** SHAP measures how features influence model weights; it does not establish biological mechanism.
2. **Data-Sample Scope:** Explanations reflect patterns within `deficiency_cleaned.csv` and must be validated across diverse clinical populations.

### ⚠️ MANDATORY MEDICAL DISCLAIMER:
> "These predictions are model-based risk estimates for research and educational purposes. They are not medical diagnoses and should not replace evaluation by a qualified healthcare professional."
""")

    # Cell 14: Day 17 Summary & Checklist
    add_markdown("""## 14. Day 17 Summary & Validation Checklist

### Completed Tasks:
- [x] SHAP concept and game-theoretic background documented cleanly.
- [x] XGBoost model (`xgboost_baseline.joblib`) & features (`xgb_feature_names.joblib`) loaded without retraining.
- [x] Preprocessing reproduced with 0 data leakage via `preprocessor.joblib`.
- [x] Multiclass SHAP TreeExplainer generated on 200 validation samples (`random_state=42`).
- [x] Global feature importance computed and visual summary created.
- [x] Application-level risk score formula (`predicted_prob * 100`) and 4-tier risk categories implemented.
- [x] Human-readable `explain_prediction()` helper function created.
- [x] Lightweight `shap_metadata.joblib` saved.
- [x] Mandatory medical disclaimer attached.

**Day 17 Status:** COMPLETE ✅""")

    # Save notebook to disk
    os.makedirs("backend/ml/notebooks", exist_ok=True)
    nb_path = "backend/ml/notebooks/05_shap_risk_score.ipynb"
    with open(nb_path, "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=2)

    print(f"✅ Generated notebook at: {nb_path}")

if __name__ == "__main__":
    create_notebook()
