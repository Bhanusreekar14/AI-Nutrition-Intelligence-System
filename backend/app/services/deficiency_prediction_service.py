import os
import joblib
import pandas as pd
import numpy as np
import shap
from typing import Dict
from app.models.prediction import (
    DeficiencyPredictionRequest,
    DeficiencyPredictionResponse,
    SHAPExplanation,
    FeatureContribution,
)

# Resolve artifacts directory reliably
SERVICE_DIR = os.path.dirname(os.path.abspath(__file__))
APP_DIR = os.path.dirname(SERVICE_DIR)
BACKEND_DIR = os.path.dirname(APP_DIR)
ARTIFACTS_DIR = os.path.join(BACKEND_DIR, "ml", "artifacts")

MODEL_PATH = os.path.join(ARTIFACTS_DIR, "xgboost_baseline.joblib")
PREPROCESSOR_PATH = os.path.join(ARTIFACTS_DIR, "preprocessor.joblib")
FEATURE_NAMES_PATH = os.path.join(ARTIFACTS_DIR, "xgb_feature_names.joblib")
SHAP_METADATA_PATH = os.path.join(ARTIFACTS_DIR, "shap_metadata.joblib")

# Ensure required artifacts exist
for path in [MODEL_PATH, PREPROCESSOR_PATH, FEATURE_NAMES_PATH, SHAP_METADATA_PATH]:
    if not os.path.exists(path):
        raise RuntimeError(f"Required ML artifact missing: {path}")

# Load ML artifacts ONCE at module initialization time
try:
    xgb_model = joblib.load(MODEL_PATH)
    preprocessor = joblib.load(PREPROCESSOR_PATH)
    xgb_feature_names = joblib.load(FEATURE_NAMES_PATH)
    shap_metadata = joblib.load(SHAP_METADATA_PATH)
    _explainer = None
except Exception as e:
    raise RuntimeError(f"Failed to initialize ML prediction service artifacts: {e}")

def get_explainer():
    global _explainer
    if _explainer is None:
        _explainer = shap.TreeExplainer(xgb_model.get_booster())
    return _explainer

TARGET_MAPPING: Dict[int, str] = shap_metadata.get("target_mapping", {
    0: "Anemia",
    1: "Healthy",
    2: "Night_Blindness",
    3: "Rickets_Osteomalacia",
    4: "Scurvy"
})

MEDICAL_DISCLAIMER = (
    "These predictions are model-based risk estimates for research and educational purposes. "
    "They are not medical diagnoses and should not replace evaluation by a qualified healthcare professional."
)

def calculate_risk_score(probability: float) -> tuple[float, str]:
    """
    Converts model predicted probability (0 to 1) into an application risk score (0 to 100)
    and maps it to an application risk category level.
    """
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

def build_raw_feature_dataframe(req: DeficiencyPredictionRequest) -> pd.DataFrame:
    """
    Constructs the un-preprocessed raw feature DataFrame expected by the ColumnTransformer.
    """
    data = req.model_dump()
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
        "has_night_blindness": int(data["has_night_blindness"]),
        "has_fatigue": int(data["has_fatigue"]),
        "has_bleeding_gums": int(data["has_bleeding_gums"]),
        "has_bone_pain": int(data["has_bone_pain"]),
        "has_muscle_weakness": int(data["has_muscle_weakness"]),
        "has_numbness_tingling": int(data["has_numbness_tingling"]),
        "has_memory_problems": int(data["has_memory_problems"]),
        "has_pale_skin": int(data["has_pale_skin"]),
    }

    # One-hot encoded categorical categories matching training schema
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
        val = data.get(cat_name)
        for cv in cat_values:
            col_name = f"{cat_name}_{cv}"
            row[col_name] = 1 if val == cv else 0

    return pd.DataFrame([row])

class DeficiencyPredictionService:
    @staticmethod
    def predict(req: DeficiencyPredictionRequest) -> DeficiencyPredictionResponse:
        # 1. Build raw input DataFrame
        df_raw = build_raw_feature_dataframe(req)

        # 2. Transform using preprocessor
        X_trans = preprocessor.transform(df_raw)
        if hasattr(X_trans, "toarray"):
            X_trans = X_trans.toarray()

        df_model_input = pd.DataFrame(X_trans, columns=xgb_feature_names)

        # 3. Verify feature count and column order
        if list(df_model_input.columns) != xgb_feature_names:
            raise ValueError("Preprocessed feature ordering does not match expected model feature names.")

        # 4. Predict probabilities & determine predicted class
        probs_raw = xgb_model.predict_proba(df_model_input)[0]
        class_probs = {TARGET_MAPPING[i]: round(float(probs_raw[i]), 4) for i in range(len(TARGET_MAPPING))}
        
        pred_class_id = int(np.argmax(probs_raw))
        pred_class_name = TARGET_MAPPING[pred_class_id]
        pred_probability = round(float(probs_raw[pred_class_id]), 4)

        # 5. Calculate risk score & risk level
        risk_score, risk_level = calculate_risk_score(pred_probability)

        # 6. SHAP feature attribution
        explainer_instance = get_explainer()
        shap_values = explainer_instance(df_model_input)
        if len(shap_values.shape) == 3:
            feature_shaps = shap_values.values[0, :, pred_class_id]
        else:
            feature_shaps = shap_values.values[0]

        impacts = pd.DataFrame({
            "feature": xgb_feature_names,
            "contribution": feature_shaps
        }).sort_values(by="contribution", key=abs, ascending=False)

        top_pos = [
            FeatureContribution(feature=row["feature"], contribution=round(float(row["contribution"]), 4))
            for _, row in impacts[impacts["contribution"] > 0].head(5).iterrows()
        ]

        top_neg = [
            FeatureContribution(feature=row["feature"], contribution=round(float(row["contribution"]), 4))
            for _, row in impacts[impacts["contribution"] < 0].head(5).iterrows()
        ]

        explanation = SHAPExplanation(
            top_positive_features=top_pos,
            top_negative_features=top_neg
        )

        return DeficiencyPredictionResponse(
            predicted_class=pred_class_name,
            predicted_probability=pred_probability,
            risk_score=risk_score,
            risk_level=risk_level,
            class_probabilities=class_probs,
            explanation=explanation,
            medical_disclaimer=MEDICAL_DISCLAIMER
        )
