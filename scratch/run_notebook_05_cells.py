import joblib
import pandas as pd
import numpy as np
import os
import shap

print("--- Running Notebook 05 Cells Execution Test (Fast 50-sample validation) ---", flush=True)

MODEL_PATH = "backend/ml/artifacts/xgboost_baseline.joblib"
FEATURE_NAMES_PATH = "backend/ml/artifacts/xgb_feature_names.joblib"
PREPROCESSOR_PATH = "backend/ml/artifacts/preprocessor.joblib"

xgb_model = joblib.load(MODEL_PATH)
xgb_feature_names = joblib.load(FEATURE_NAMES_PATH)
preprocessor = joblib.load(PREPROCESSOR_PATH)

print(f"✅ Loaded XGBoost Model: {type(xgb_model).__name__}", flush=True)
print(f"✅ Loaded Feature Names: {len(xgb_feature_names)} features", flush=True)

DATASET_PATH = "datasets/deficiency/deficiency_cleaned.csv"
df = pd.read_csv(DATASET_PATH)

TARGET_MAPPING = {
    0: "Anemia",
    1: "Healthy",
    2: "Night_Blindness",
    3: "Rickets_Osteomalacia",
    4: "Scurvy"
}

X = df.drop(columns=["disease_diagnosis"])
y = df["disease_diagnosis"]

X_trans = preprocessor.transform(X)
if hasattr(X_trans, "toarray"):
    X_trans = X_trans.toarray()

X_df = pd.DataFrame(X_trans, columns=xgb_feature_names)
assert list(X_df.columns) == xgb_feature_names

# Sample 50 samples for fast execution
sample_X = X_df.sample(n=50, random_state=42)
sample_y = y.loc[sample_X.index]

explainer = shap.TreeExplainer(xgb_model)
shap_explanation = explainer(sample_X)

num_samples, num_features, num_classes = shap_explanation.shape
print(f"✅ SHAP Values Shape: {shap_explanation.shape} (Samples: {num_samples}, Features: {num_features}, Classes: {num_classes})", flush=True)

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

for p in [0.12, 0.45, 0.73, 0.94]:
    sc, lv = calculate_risk_score(p)
    print(f"Prob: {p:.2f} -> Score: {sc:5.2f} -> Category: {lv}", flush=True)

shap_metadata = {
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

METADATA_PATH = "backend/ml/artifacts/shap_metadata.joblib"
joblib.dump(shap_metadata, METADATA_PATH)
meta_size = os.path.getsize(METADATA_PATH)
print(f"✅ Saved SHAP metadata artifact to: {METADATA_PATH} ({meta_size} bytes)", flush=True)
print("SUCCESS: Notebook execution verified!", flush=True)
