from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class HealthProfileBase(BaseModel):
    age: int = Field(..., gt=0, lt=120, description="Age in years")
    gender: str = Field(..., description="male, female, other, prefer_not_to_say")
    height_cm: float = Field(..., gt=0, description="Height in centimeters")
    weight_kg: float = Field(..., gt=0, description="Weight in kilograms")
    activity_level: str = Field(
        ..., 
        description="sedentary, lightly_active, moderately_active, very_active, extra_active"
    )
    dietary_preference: str = Field(
        default="omnivore",
        description="omnivore, vegetarian, vegan, keto, paleo, mediterranean, other"
    )
    health_goals: List[str] = Field(default=[], description="List of health goals")
    allergies_intolerances: List[str] = Field(default=[], description="List of allergies")
    medical_conditions: List[str] = Field(default=[], description="List of medical conditions")

class HealthProfileCreate(HealthProfileBase):
    pass

class HealthProfileUpdate(BaseModel):
    age: Optional[int] = None
    gender: Optional[str] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    activity_level: Optional[str] = None
    dietary_preference: Optional[str] = None
    health_goals: Optional[List[str]] = None
    allergies_intolerances: Optional[List[str]] = None
    medical_conditions: Optional[List[str]] = None

class HealthProfileResponse(HealthProfileBase):
    id: str
    user_id: str
    bmr: Optional[float] = None
    tdee: Optional[float] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
