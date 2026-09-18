from pydantic import BaseModel, Field
from typing import List, Optional, Union

class RecommendedFood(BaseModel):
    fdc_id: Optional[int] = Field(default=None, description="USDA Food Data Central ID")
    food_name: str = Field(..., description="Food item name")
    food_category: Optional[str] = Field(default=None, description="Food category classification")
    serving_size: Optional[float] = Field(default=None, description="Serving size numeric value")
    serving_unit: Optional[str] = Field(default=None, description="Serving size unit (e.g. g, oz)")
    calories: Optional[float] = Field(default=None, description="Energy content in kcal")
    protein_g: Optional[float] = Field(default=None, description="Protein in grams")
    carbs_g: Optional[float] = Field(default=None, description="Total carbohydrates in grams")
    fat_g: Optional[float] = Field(default=None, description="Total fat in grams")
    fiber_g: Optional[float] = Field(default=None, description="Dietary fiber in grams")
    iron_mg: Optional[float] = Field(default=None, description="Iron in milligrams")
    vitamin_c_mg: Optional[float] = Field(default=None, description="Vitamin C in milligrams")
    calcium_mg: Optional[float] = Field(default=None, description="Calcium in milligrams")
    health_score: Optional[int] = Field(default=None, description="USDA / Nutrition Health Score (0-100)")
    ranking_score: float = Field(..., description="Internal deterministic ranking score (0-100)")
    recommendation_reason: str = Field(..., description="Factual recommendation rationale")

class DietRecommendationRequest(BaseModel):
    predicted_class: str = Field(
        ...,
        description="Predicted deficiency class (Anemia, Scurvy, Rickets_Osteomalacia, Night_Blindness, Healthy)"
    )
    risk_level: str = Field(default="Moderate Risk", description="Application risk level string")
    risk_score: float = Field(default=50.0, ge=0.0, le=100.0, description="Risk score numeric value")
    dietary_preference: str = Field(
        default="omnivore",
        description="Dietary preference (omnivore, vegetarian, vegan, keto, paleo)"
    )
    allergies_intolerances: Union[List[str], str] = Field(
        default=[],
        description="List or comma-separated string of user allergies/intolerances"
    )
    limit: int = Field(default=10, ge=1, le=50, description="Maximum number of recommended food items")

class DietRecommendationResponse(BaseModel):
    predicted_class: str = Field(..., description="Predicted deficiency diagnosis class")
    risk_level: str = Field(..., description="Evaluated risk level")
    risk_score: float = Field(..., description="Evaluated risk score")
    targeted_nutrients: List[str] = Field(..., description="List of targeted nutrients or rule signals")
    recommended_foods: List[RecommendedFood] = Field(..., description="List of top ranked food recommendations")
    dietary_advice: List[str] = Field(..., description="Educational dietary guidance notes")
    medical_disclaimer: str = Field(..., description="Mandatory medical research/educational disclaimer")
