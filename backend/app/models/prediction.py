from pydantic import BaseModel, Field
from typing import Dict, List

class FeatureContribution(BaseModel):
    feature: str = Field(..., description="Name of the feature")
    contribution: float = Field(..., description="SHAP contribution value")

class SHAPExplanation(BaseModel):
    top_positive_features: List[FeatureContribution] = Field(
        default=[], description="Top features increasing the predicted deficiency risk"
    )
    top_negative_features: List[FeatureContribution] = Field(
        default=[], description="Top features decreasing the predicted deficiency risk"
    )

class DeficiencyPredictionRequest(BaseModel):
    # Demographics & Anthropometrics
    age: float = Field(..., gt=0, lt=120, description="Age in years")
    bmi: float = Field(..., gt=0, lt=100, description="Body Mass Index")

    # Dietary Micronutrient Percent RDAs (>= 0)
    vitamin_a_percent_rda: float = Field(default=100.0, ge=0, description="Vitamin A (% of RDA)")
    vitamin_c_percent_rda: float = Field(default=100.0, ge=0, description="Vitamin C (% of RDA)")
    vitamin_d_percent_rda: float = Field(default=100.0, ge=0, description="Vitamin D (% of RDA)")
    vitamin_e_percent_rda: float = Field(default=100.0, ge=0, description="Vitamin E (% of RDA)")
    vitamin_b12_percent_rda: float = Field(default=100.0, ge=0, description="Vitamin B12 (% of RDA)")
    folate_percent_rda: float = Field(default=100.0, ge=0, description="Folate (% of RDA)")
    calcium_percent_rda: float = Field(default=100.0, ge=0, description="Calcium (% of RDA)")
    iron_percent_rda: float = Field(default=100.0, ge=0, description="Iron (% of RDA)")

    # Lab Biomarkers (>= 0)
    hemoglobin_g_dl: float = Field(default=13.5, ge=0, description="Hemoglobin (g/dL)")
    serum_vitamin_d_ng_ml: float = Field(default=30.0, ge=0, description="Serum Vitamin D (ng/mL)")
    serum_vitamin_b12_pg_ml: float = Field(default=400.0, ge=0, description="Serum Vitamin B12 (pg/mL)")
    serum_folate_ng_ml: float = Field(default=12.0, ge=0, description="Serum Folate (ng/mL)")

    # Symptoms Count & Flags
    symptoms_count: int = Field(default=0, ge=0, description="Total active symptoms count")
    has_night_blindness: bool = Field(default=False, description="Presence of night blindness")
    has_fatigue: bool = Field(default=False, description="Presence of fatigue")
    has_bleeding_gums: bool = Field(default=False, description="Presence of bleeding gums")
    has_bone_pain: bool = Field(default=False, description="Presence of bone pain")
    has_muscle_weakness: bool = Field(default=False, description="Presence of muscle weakness")
    has_numbness_tingling: bool = Field(default=False, description="Presence of numbness or tingling")
    has_memory_problems: bool = Field(default=False, description="Presence of memory problems")
    has_pale_skin: bool = Field(default=False, description="Presence of pale skin")

    # Categorical & Lifestyle Inputs
    gender: str = Field(default="Male", description="Female, Male")
    smoking_status: str = Field(default="Never", description="Current, Former, Never")
    alcohol_consumption: str = Field(default="Unknown", description="Heavy, Moderate, Unknown")
    exercise_level: str = Field(default="Moderate", description="Active, Light, Moderate, Sedentary")
    diet_type: str = Field(default="Omnivore", description="Omnivore, Pescatarian, Vegan, Vegetarian")
    sun_exposure: str = Field(default="Moderate", description="High, Low, Moderate")
    income_level: str = Field(default="Middle", description="High, Low, Middle")
    latitude_region: str = Field(default="Mid", description="High, Low, Mid")

class DeficiencyPredictionResponse(BaseModel):
    predicted_class: str = Field(..., description="Predicted deficiency diagnosis class")
    predicted_probability: float = Field(..., ge=0.0, le=1.0, description="Probability of predicted class")
    risk_score: float = Field(..., ge=0.0, le=100.0, description="Application-level risk score (0-100)")
    risk_level: str = Field(..., description="Low Risk, Moderate Risk, High Risk, Very High Risk")
    class_probabilities: Dict[str, float] = Field(..., description="Probabilities for all 5 deficiency classes")
    explanation: SHAPExplanation = Field(..., description="SHAP feature attribution breakdown")
    medical_disclaimer: str = Field(..., description="Mandatory research/educational medical disclaimer")
