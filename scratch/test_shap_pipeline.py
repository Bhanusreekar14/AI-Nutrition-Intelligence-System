import joblib
import pandas as pd
import numpy as np
import shap

print("--- Testing SHAP Pipeline for Day 17 ---")

# 1. Load artifacts
xgb_model = joblib.load("backend/ml/artifacts/xgboost_baseline.joblib")
xgb_feature_names = joblib.load("backend/ml/artifacts/xgb_feature_names.joblib")
preprocessor = joblib.load("backend/ml/artifacts/preprocessor.joblib")

print(f"✅ Loaded XGBoost Model: {type(xgb_model)}")
print(f"✅ Loaded Feature Names: {len(xgb_feature_names)} features")
print(f"✅ Loaded Preprocessor: {type(preprocessor)}")

# 2. Load dataset
df = pd.read_csv("datasets/deficiency/deficiency_cleaned.csv")
print(f"✅ Loaded Dataset: {df.shape[0]} rows x {df.shape[1]} columns")

X = df.drop(columns=["disease_diagnosis"])
y = df["disease_diagnosis"]

# Target mapping
target_mapping = {
    0: "Anemia",
    1: "Healthy",
    2: "Night_Blindness",
    3: "Rickets_Osteomalacia",
    4: "Scurvy"
}

# 3. Transform data using saved preprocessor
X_trans = preprocessor.transform(X)
if hasattr(X_trans, "toarray"):
    X_trans = X_trans.toarray()

df_features = pd.DataFrame(X_trans, columns=xgb_feature_names)
print(f"✅ Transformed feature matrix shape: {df_features.shape}")

# 4. Take a representative sample (e.g. 200 samples) with random_state=42
sample_df = df_features.sample(n=200, random_state=42)

# 5. Initialize SHAP TreeExplainer
explainer = shap.TreeExplainer(xgb_model)
shap_values = explainer(sample_df)

print(f"✅ SHAP Version: {shap.__version__}")
print(f"✅ SHAP Output Type: {type(shap_values)}")
print(f"✅ SHAP Values Shape: {shap_values.shape}")
print(f"   (Samples: {shap_values.shape[0]}, Features: {shap_values.shape[1]}, Classes: {shap_values.shape[2] if len(shap_values.shape) > 2 else 1})")

# 6. Test Risk Score Helper Function
def calculate_risk_score(probability: float):
    score = round(probability * 100, 2)
    if score < 30:
        level = "Low Risk"
    elif score < 60:
        level = "Moderate Risk"
    elif score < 80:
        level = "High Risk"
    else:
        level = "Very High Risk"
    return score, level

print("\n--- Testing Risk Score Function ---")
for p in [0.15, 0.45, 0.72, 0.95]:
    score, level = calculate_risk_score(p)
    print(f"Prob: {p:.2f} -> Score: {score} -> Level: {level}")

# 7. Test Explanation Generator for a sample prediction
idx = 0
sample_input = sample_df.iloc[[idx]]
pred_class_id = xgb_model.predict(sample_input)[0]
pred_probs = xgb_model.predict_proba(sample_input)[0]
pred_prob = pred_probs[pred_class_id]
pred_disease = target_mapping[pred_class_id]
risk_score, risk_level = calculate_risk_score(pred_prob)

# SHAP values for predicted class
if len(shap_values.shape) == 3:
    instance_shap = shap_values.values[idx, :, pred_class_id]
else:
    instance_shap = shap_values.values[idx]

feature_impacts = pd.DataFrame({
    'feature': xgb_feature_names,
    'shap_value': instance_shap,
    'feature_value': sample_input.iloc[0].values
}).sort_values(by='shap_value', key=abs, ascending=False)

top_positive = feature_impacts[feature_impacts['shap_value'] > 0].head(3)
top_negative = feature_impacts[feature_impacts['shap_value'] < 0].head(3)

print("\n--- Testing Explanation Generator ---")
print(f"Predicted Class: {pred_disease} (Class {pred_class_id})")
print(f"Confidence: {pred_prob * 100:.2f}%")
print(f"Application Risk Score: {risk_score} ({risk_level})")
print("\nTop Positive SHAP Contributors (increasing risk of this diagnosis):")
for _, row in top_positive.iterrows():
    print(f"  • {row['feature']}: SHAP = {row['shap_value']:+.4f} (val = {row['feature_value']:.2f})")

print("\nTop Negative SHAP Contributors (decreasing risk of this diagnosis):")
for _, row in top_negative.iterrows():
    print(f"  • {row['feature']}: SHAP = {row['shap_value']:+.4f} (val = {row['feature_value']:.2f})")

print("\nSUCCESS: All pipeline components passed!")
