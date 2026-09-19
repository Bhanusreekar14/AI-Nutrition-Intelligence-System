from enum import Enum
from typing import List, Dict, Optional
from pydantic import BaseModel, Field
from app.models.recommendation import RecommendedFood

class MealType(str, Enum):
    BREAKFAST = "breakfast"
    LUNCH = "lunch"
    SNACK = "snack"
    DINNER = "dinner"

class MealSelectionConstraints(BaseModel):
    target_counts: Dict[MealType, int] = Field(
        default_factory=lambda: {
            MealType.BREAKFAST: 2,
            MealType.LUNCH: 2,
            MealType.SNACK: 1,
            MealType.DINNER: 2,
        },
        description="Target number of food items selected per meal type"
    )
    max_food_repetition_per_day: int = Field(
        default=1,
        ge=1,
        description="Maximum allowed occurrences of the exact same food item in a single day"
    )
    max_category_repetition_per_day: int = Field(
        default=2,
        ge=1,
        description="Maximum allowed occurrences of foods from the same category in a single day"
    )
    enforce_category_diversity: bool = Field(
        default=True,
        description="Whether to encourage category diversity across meals"
    )

class MealSelection(BaseModel):
    meal_type: MealType = Field(..., description="Type of meal (breakfast, lunch, snack, dinner)")
    target_count: int = Field(..., description="Target number of items for this meal")
    selected_foods: List[RecommendedFood] = Field(default_factory=list, description="Foods assigned to this meal")

class DailyMealPlan(BaseModel):
    day: int = Field(default=1, ge=1, description="Day number of the meal plan")
    meals: Dict[MealType, MealSelection] = Field(..., description="Mapping of meal types to selected foods")
    total_calories: float = Field(default=0.0, description="Sum of calories for the day in kcal")
    total_protein_g: float = Field(default=0.0, description="Sum of protein for the day in grams")
    total_carbs_g: float = Field(default=0.0, description="Sum of total carbohydrates for the day in grams")
    total_fat_g: float = Field(default=0.0, description="Sum of total fat for the day in grams")
    total_fiber_g: float = Field(default=0.0, description="Sum of dietary fiber for the day in grams")
    deficiency_class: str = Field(..., description="Target deficiency class profile")
    medical_disclaimer: str = Field(..., description="Mandatory medical educational disclaimer")

class WeeklyMealPlanConstraints(BaseModel):
    max_weekly_food_repetition: int = Field(
        default=2,
        ge=1,
        description="Maximum allowed occurrences of a food item across the entire 7-day plan"
    )
    max_consecutive_day_repetition: int = Field(
        default=1,
        ge=1,
        description="Maximum allowed occurrences of the same food item on consecutive days"
    )
    max_weekly_category_repetition: int = Field(
        default=6,
        ge=1,
        description="Maximum allowed occurrences of the same food category across the 7-day plan"
    )
    daily_constraints: Optional[MealSelectionConstraints] = Field(
        default=None,
        description="Optional override constraints for single-day meal selection"
    )

class WeeklyMealPlan(BaseModel):
    plan_id: Optional[str] = Field(default=None, description="Generated unique plan identifier string")
    days: List[DailyMealPlan] = Field(..., description="List of 7 DailyMealPlan objects")
    total_days: int = Field(default=7, description="Total days in the generated plan")
    total_weekly_calories: float = Field(default=0.0, description="Sum of calories across all 7 days in kcal")
    total_weekly_protein_g: float = Field(default=0.0, description="Sum of protein across all 7 days in grams")
    total_weekly_carbs_g: float = Field(default=0.0, description="Sum of carbs across all 7 days in grams")
    total_weekly_fat_g: float = Field(default=0.0, description="Sum of fat across all 7 days in grams")
    total_weekly_fiber_g: float = Field(default=0.0, description="Sum of dietary fiber across all 7 days in grams")
    deficiency_class: str = Field(..., description="Target deficiency class profile")
    medical_disclaimer: str = Field(..., description="Mandatory medical educational disclaimer")

