import os
import hashlib
import time
import sys

sys.path.insert(0, os.path.abspath("backend"))

from app.models.prediction import DeficiencyPredictionRequest
from app.services.deficiency_prediction_service import DeficiencyPredictionService

print("--- Artifact Integrity & Performance Benchmark ---", flush=True)

artifacts = {
    "cleaned_dataset": "datasets/deficiency/deficiency_cleaned.csv",
    "preprocessor": "backend/ml/artifacts/preprocessor.joblib",
    "xgboost_model": "backend/ml/artifacts/xgboost_baseline.joblib",
    "feature_names": "backend/ml/artifacts/xgb_feature_names.joblib",
    "shap_metadata": "backend/ml/artifacts/shap_metadata.joblib",
    "supabase_migration": "supabase/migrations/20260909175500_enable_rls_for_user_data.sql"
}

print("\n1. ARTIFACT INTEGRITY CHECK (MD5 Hashes):")
for name, path in artifacts.items():
    if os.path.exists(path):
        with open(path, "rb") as f:
            h = hashlib.md5(f.read()).hexdigest()
        print(f"  • {name:20s}: {h} ({os.path.getsize(path)} bytes)")
    else:
        print(f"  • {name:20s}: MISSING!")

payload = DeficiencyPredictionRequest(
    age=35.0,
    bmi=22.5,
    vitamin_a_percent_rda=85.0,
    vitamin_c_percent_rda=90.0,
    vitamin_d_percent_rda=40.0,
    vitamin_e_percent_rda=75.0,
    vitamin_b12_percent_rda=60.0,
    folate_percent_rda=80.0,
    calcium_percent_rda=70.0,
    iron_percent_rda=50.0,
    hemoglobin_g_dl=11.5,
    serum_vitamin_d_ng_ml=18.0,
    serum_vitamin_b12_pg_ml=250.0,
    serum_folate_ng_ml=8.0,
    symptoms_count=2,
    has_night_blindness=False,
    has_fatigue=True,
    has_bleeding_gums=False,
    has_bone_pain=True,
    has_muscle_weakness=False,
    has_numbness_tingling=False,
    has_memory_problems=False,
    has_pale_skin=False,
    gender="Female",
    smoking_status="Never",
    alcohol_consumption="Moderate",
    exercise_level="Moderate",
    diet_type="Vegetarian",
    sun_exposure="Low",
    income_level="Middle",
    latitude_region="Mid"
)

print("\n2. PERFORMANCE BENCHMARK (Prediction + SHAP Explanation):")
t0 = time.time()
res_first = DeficiencyPredictionService.predict(payload)
t1 = time.time()
first_latency = (t1 - t0) * 1000.0
print(f"  • First Prediction Latency: {first_latency:.2f} ms")

latencies = []
for _ in range(20):
    t_start = time.time()
    _ = DeficiencyPredictionService.predict(payload)
    t_end = time.time()
    latencies.append((t_end - t_start) * 1000.0)

avg_latency = sum(latencies) / len(latencies)
min_latency = min(latencies)
max_latency = max(latencies)

print(f"  • Average Subsequent Latency (20 runs): {avg_latency:.2f} ms")
print(f"  • Min Latency: {min_latency:.2f} ms")
print(f"  • Max Latency: {max_latency:.2f} ms")

print("\nSUCCESS: All benchmarks completed cleanly!")
