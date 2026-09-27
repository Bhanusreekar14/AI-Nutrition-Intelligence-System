from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any

class PredictionHistoryEntry(BaseModel):
    id: str = Field(..., description="Unique record identifier")
    user_id: str = Field(..., description="Authenticated user ID")
    predicted_class: str = Field(..., description="Predicted deficiency diagnosis class")
    predicted_probability: float = Field(..., description="Probability of predicted class")
    risk_score: float = Field(..., description="Risk score (0-100)")
    risk_level: str = Field(..., description="Risk level classification")
    class_probabilities: Dict[str, float] = Field(default_factory=dict, description="Probabilities for all deficiency classes")
    shap_positive_features: List[Dict[str, Any]] = Field(default_factory=list, description="SHAP positive features")
    shap_negative_features: List[Dict[str, Any]] = Field(default_factory=list, description="SHAP negative features")
    symptoms_count: int = Field(default=0, description="Active symptoms count at prediction time")
    serum_hemoglobin_g_dl: Optional[float] = Field(default=None, description="Hemoglobin (g/dL)")
    serum_vitamin_d_ng_ml: Optional[float] = Field(default=None, description="Serum Vitamin D (ng/mL)")
    serum_vitamin_b12_pg_ml: Optional[float] = Field(default=None, description="Serum Vitamin B12 (pg/mL)")
    serum_iron_ug_dl: Optional[float] = Field(default=None, description="Serum Iron (ug/dL)")
    serum_calcium_mg_dl: Optional[float] = Field(default=None, description="Serum Calcium (mg/dL)")
    serum_folate_ng_ml: Optional[float] = Field(default=None, description="Serum Folate (ng/mL)")
    recorded_at: str = Field(..., description="Timestamp when prediction was recorded")
    model_version: Optional[str] = Field(default="v1.0.0", description="ML model version")

class BiomarkerTrendPoint(BaseModel):
    date: str = Field(..., description="Measurement date (YYYY-MM-DD)")
    hemoglobin: Optional[float] = Field(default=None)
    vitamin_d: Optional[float] = Field(default=None)
    vitamin_b12: Optional[float] = Field(default=None)
    iron: Optional[float] = Field(default=None)
    calcium: Optional[float] = Field(default=None)
    folate: Optional[float] = Field(default=None)

class SymptomTrendPoint(BaseModel):
    date: str = Field(..., description="Assessment date (YYYY-MM-DD)")
    symptoms_count: int = Field(default=0)

class PredictionProgressResponse(BaseModel):
    status: str = Field(..., description="Progress status: 'complete' or 'insufficient_history'")
    message: str = Field(..., description="Human readable summary or insufficient data message")
    selected_weeks: int = Field(..., description="Evaluation window in weeks (4, 8, or 12)")
    total_snapshots: int = Field(..., description="Total prediction snapshots in selected window")
    first_risk_score: Optional[float] = Field(default=None, description="Baseline risk score in window")
    latest_risk_score: Optional[float] = Field(default=None, description="Latest risk score in window")
    risk_score_change: Optional[float] = Field(default=None, description="Absolute risk score change (latest - first)")
    percentage_change: Optional[float] = Field(default=None, description="Percentage change where valid")
    first_risk_level: Optional[str] = Field(default=None, description="Baseline risk level")
    latest_risk_level: Optional[str] = Field(default=None, description="Latest risk level")
    risk_level_changed: Optional[bool] = Field(default=None, description="Whether risk level changed")
    transition_text: Optional[str] = Field(default=None, description="Human readable transition text (e.g. High Risk -> Moderate Risk)")
    chronological_history: List[PredictionHistoryEntry] = Field(default_factory=list)
    class_distribution: Dict[str, int] = Field(default_factory=dict)
    symptom_trend: List[SymptomTrendPoint] = Field(default_factory=list)
    biomarker_trend: List[BiomarkerTrendPoint] = Field(default_factory=list)
    available_biomarkers: List[str] = Field(default_factory=list)
