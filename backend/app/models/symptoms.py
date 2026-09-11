from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime

class SymptomItem(BaseModel):
    symptom: str = Field(..., description="Fatigue, Hair Loss, Skin Conditions, Muscle Weakness, Mood-related Symptoms")
    severity: str = Field(..., description="Never, Sometimes, Often, Very Often")

class SymptomAssessmentCreate(BaseModel):
    assessment_date: date = Field(default_factory=date.today)
    assessments: List[SymptomItem]

class SymptomAssessmentResponse(BaseModel):
    id: str
    user_id: str
    symptom: str
    severity: str
    assessment_date: date
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
