from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import date, datetime

class FoodDiaryBase(BaseModel):
    logged_date: date
    meal_type: str = Field(..., description="breakfast, lunch, dinner, snack")
    food_name: str
    serving_size: float = Field(default=1.0, gt=0)
    serving_unit: str = Field(default="g")
    calories: float = Field(default=0.0, ge=0)
    protein_g: float = Field(default=0.0, ge=0)
    carbs_g: float = Field(default=0.0, ge=0)
    fat_g: float = Field(default=0.0, ge=0)
    micros_json: Optional[Dict[str, Any]] = Field(default={})

class FoodDiaryCreate(FoodDiaryBase):
    pass

class FoodDiaryResponse(FoodDiaryBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class DailyNutritionSummary(BaseModel):
    logged_date: date
    total_calories: float
    total_protein_g: float
    total_carbs_g: float
    total_fat_g: float
    entry_count: int
