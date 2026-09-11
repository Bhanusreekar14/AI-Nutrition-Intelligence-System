import joblib
import pandas as pd
import numpy as np

# Load artifacts
preprocessor = joblib.load("backend/ml/artifacts/preprocessor.joblib")
xgb_model = joblib.load("backend/ml/artifacts/xgboost_baseline.joblib")
xgb_feature_names = joblib.load("backend/ml/artifacts/xgb_feature_names.joblib")

print("--- Testing API Request to Feature Matrix Conversion ---")

# Example raw API input dict (as sent by user or Pydantic schema)
api_input = {
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
    "has_night_blindness": 0,
    "has_fatigue": 1,
    "has_bleeding_gums": 0,
    "has_bone_pain": 1,
    "has_muscle_weakness": 0,
    "has_numbness_tingling": 0,
    "has_memory_problems": 0,
    "has_pale_skin": 0,
    "gender": "Female",
    "smoking_status": "Never",
    "alcohol_consumption": "Moderate",
    "exercise_level": "Moderate",
    "diet_type": "Vegetarian",
    "sun_exposure": "Low",
    "income_level": "Middle",
    "latitude_region": "Mid"
}

def build_raw_feature_row(data: dict) -> pd.DataFrame:
    # 1. Numerical & binary symptoms
    row = {
        "age": data["age"],
        "bmi": data["bmi"],
        "vitamin_a_percent_rda": data["vitamin_a_percent_rda"],
        "vitamin_c_percent_rda": data["vitamin_c_percent_rda"],
        "vitamin_d_percent_rda": data["vitamin_d_percent_rda"],
        "vitamin_e_percent_rda": data["vitamin_e_percent_rda"],
        "vitamin_b12_percent_rda": data["vitamin_b12_percent_rda"],
        "folate_percent_rda": data["folate_percent_rda"],
        "calcium_percent_rda": data["calcium_percent_rda"],
        "iron_percent_rda": data["iron_percent_rda"],
        "hemoglobin_g_dl": data["hemoglobin_g_dl"],
        "serum_vitamin_d_ng_ml": data["serum_vitamin_d_ng_ml"],
        "serum_vitamin_b12_pg_ml": data["serum_vitamin_b12_pg_ml"],
        "serum_folate_ng_ml": data["serum_folate_ng_ml"],
        "symptoms_count": data["symptoms_count"],
        "has_night_blindness": int(data.get("has_night_blindness", 0)),
        "has_fatigue": int(data.get("has_fatigue", 0)),
        "has_bleeding_gums": int(data.get("has_bleeding_gums", 0)),
        "has_bone_pain": int(data.get("has_bone_pain", 0)),
        "has_muscle_weakness": int(data.get("has_muscle_weakness", 0)),
        "has_numbness_tingling": int(data.get("has_numbness_tingling", 0)),
        "has_memory_problems": int(data.get("has_memory_problems", 0)),
        "has_pale_skin": int(data.get("has_pale_skin", 0)),
    }

    # 2. Map categorical fields to one-hot columns
    categories = {
        "gender": ["Female", "Male"],
        "smoking_status": ["Current", "Former", "Never"],
        "alcohol_consumption": ["Heavy", "Moderate", "Unknown"],
        "exercise_level": ["Active", "Light", "Moderate", "Sedentary"],
        "diet_type": ["Omnivore", "Pescatarian", "Vegan", "Vegetarian"],
        "sun_exposure": ["High", "Low", "Moderate"],
        "income_level": ["High", "Low", "Middle"],
        "latitude_region": ["High", "Low", "Mid"]
    }

    for cat_name, cat_values in categories.items():
        val = data.get(cat_name, cat_values[0])
        for cv in cat_values:
            col_name = f"{cat_name}_{cv}"
            row[col_name] = 1 if val == cv else 0

    df_raw = pd.DataFrame([row])
    return df_raw

df_raw = build_raw_feature_row(api_input)
print("Built raw feature dataframe shape:", df_raw.shape)

# Transform using preprocessor
X_trans = preprocessor.transform(df_raw)
if hasattr(X_trans, "toarray"):
    X_trans = X_trans.toarray()

df_model_input = pd.DataFrame(X_trans, columns=xgb_feature_names)
print("Transformed model input dataframe shape:", df_model_input.shape)
assert list(df_model_input.columns) == xgb_feature_names, "Feature ordering mismatch!"

# Run prediction
pred_class_id = int(xgb_model.predict(df_model_input)[0])
pred_probs = xgb_model.predict_proba(df_model_input)[0]

print(f"Predicted class ID: {pred_class_id}")
print("Probabilities:", pred_probs)
print("SUCCESS: Conversion and prediction work perfectly!")
