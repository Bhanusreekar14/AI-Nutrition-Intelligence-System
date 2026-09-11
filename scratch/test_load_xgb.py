import joblib
import sys

print("Loading preprocessor...", flush=True)
prep = joblib.load("backend/ml/artifacts/preprocessor.joblib")
print(f"Loaded preprocessor: {type(prep)}", flush=True)

print("Loading xgb_feature_names...", flush=True)
feats = joblib.load("backend/ml/artifacts/xgb_feature_names.joblib")
print(f"Loaded xgb_feature_names: {len(feats)} features", flush=True)

print("Loading xgboost_baseline...", flush=True)
xgb = joblib.load("backend/ml/artifacts/xgboost_baseline.joblib")
print(f"Loaded xgboost_baseline: {type(xgb)}", flush=True)
