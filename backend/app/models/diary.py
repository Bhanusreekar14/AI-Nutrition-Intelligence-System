from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import date, datetime

class FoodDiaryBase(BaseModel):
    logged_date: date
    meal_type: str = Field(..., description="breakfast, lunch, dinner, snack")
    food_name: str
    external_food_id: Optional[str] = None
    source: Optional[str] = "manual"
    serving_size: float = Field(default=1.0, gt=0)
    serving_unit: str = Field(default="g")
    calories: float = Field(default=0.0, ge=0)
    protein_g: float = Field(default=0.0, ge=0)
    carbs_g: float = Field(default=0.0, ge=0)
    fat_g: float = Field(default=0.0, ge=0)
    fiber_g: float = Field(default=0.0, ge=0)
    sugar_g: float = Field(default=0.0, ge=0)
    sodium_mg: float = Field(default=0.0, ge=0)
    vitamin_d_mcg: float = Field(default=0.0, ge=0)
    vitamin_b12_mcg: float = Field(default=0.0, ge=0)
    iron_mg: float = Field(default=0.0, ge=0)
    calcium_mg: float = Field(default=0.0, ge=0)
    micros_json: Optional[Dict[str, Any]] = Field(default={})

class FoodDiaryCreate(FoodDiaryBase):
    pass

class FoodDiaryUpdate(BaseModel):
    logged_date: Optional[date] = None
    meal_type: Optional[str] = None
    food_name: Optional[str] = None
    serving_size: Optional[float] = None
    serving_unit: Optional[str] = None
    calories: Optional[float] = None
    protein_g: Optional[float] = None
    carbs_g: Optional[float] = None
    fat_g: Optional[float] = None
    fiber_g: Optional[float] = None
    sugar_g: Optional[float] = None
    sodium_mg: Optional[float] = None
    vitamin_d_mcg: Optional[float] = None
    vitamin_b12_mcg: Optional[float] = None
    iron_mg: Optional[float] = None
    calcium_mg: Optional[float] = None

class FoodDiaryResponse(FoodDiaryBase):
    id: str
    user_id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class DailyNutritionSummary(BaseModel):
    logged_date: date
    total_calories: float
    total_protein_g: float
    total_carbs_g: float
    total_fat_g: float
    total_fiber_g: float
    total_sugar_g: float
    total_sodium_mg: float
    total_vitamin_d_mcg: float
    total_vitamin_b12_mcg: float
    total_iron_mg: float
    total_calcium_mg: float
    entry_count: int
