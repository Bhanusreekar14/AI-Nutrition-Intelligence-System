import joblib
import pandas as pd
import shap
import time

print("--- Testing SHAP TreeExplainer Speed ---", flush=True)

xgb_model = joblib.load("backend/ml/artifacts/xgboost_baseline.joblib")
preprocessor = joblib.load("backend/ml/artifacts/preprocessor.joblib")
xgb_feature_names = joblib.load("backend/ml/artifacts/xgb_feature_names.joblib")

t0 = time.time()
booster = xgb_model.get_booster()
explainer = shap.TreeExplainer(booster)
t1 = time.time()
print(f"TreeExplainer(booster) init time: {t1-t0:.4f}s", flush=True)

# Test input
sample_row = pd.DataFrame([[0]*48], columns=xgb_feature_names)
t2 = time.time()
shap_vals = explainer(sample_row)
t3 = time.time()
print(f"SHAP evaluation time: {t3-t2:.4f}s", flush=True)
print(f"SHAP shape: {shap_vals.shape}", flush=True)
