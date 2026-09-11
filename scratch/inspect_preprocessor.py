import joblib
import pandas as pd

print("--- Inspecting Dataset & Preprocessor for Day 18 ---")

df = pd.read_csv("datasets/deficiency/deficiency_cleaned.csv")
print(f"Dataset shape: {df.shape}")
print("Raw Columns:", list(df.columns))

X = df.drop(columns=["disease_diagnosis"])

preprocessor = joblib.load("backend/ml/artifacts/preprocessor.joblib")
print("\nPreprocessor type:", type(preprocessor))
print("Preprocessor transformers:")
for name, transformer, cols in preprocessor.transformers_:
    print(f"  • {name}: {type(transformer).__name__} on {cols}")

xgb_feats = joblib.load("backend/ml/artifacts/xgb_feature_names.joblib")
print(f"\nTransformed feature count: {len(xgb_feats)}")

# Test transforming 1 raw row as dict
sample_row = X.iloc[[0]]
print("\nSample raw input dict:")
print(sample_row.to_dict(orient="records")[0])
