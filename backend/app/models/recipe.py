from pydantic import BaseModel, Field
from typing import List, Optional, Union

class Recipe(BaseModel):
    recipe_id: str = Field(..., description="Unique recipe/food candidate identifier (e.g. fdc_167782)")
    fdc_id: Optional[int] = Field(default=None, description="USDA Food Data Central ID")
    title: str = Field(..., description="Food/recipe title or description")
    category: Optional[str] = Field(default=None, description="Food category classification")
    ingredients: Optional[str] = Field(default=None, description="Raw ingredients list text from dataset")
    serving_size: Optional[float] = Field(default=None, description="Serving size numeric value")
    serving_unit: Optional[str] = Field(default=None, description="Serving unit (e.g. g, oz)")
    calories: Optional[float] = Field(default=None, description="Energy in kcal")
    protein_g: Optional[float] = Field(default=None, description="Protein in grams")
    carbs_g: Optional[float] = Field(default=None, description="Carbohydrates in grams")
    fat_g: Optional[float] = Field(default=None, description="Total fat in grams")
    fiber_g: Optional[float] = Field(default=None, description="Dietary fiber in grams")
    iron_mg: Optional[float] = Field(default=None, description="Iron in milligrams")
    vitamin_c_mg: Optional[float] = Field(default=None, description="Vitamin C in milligrams")
    calcium_mg: Optional[float] = Field(default=None, description="Calcium in milligrams")
    sodium_mg: Optional[float] = Field(default=None, description="Sodium in milligrams")
    sugar_g: Optional[float] = Field(default=None, description="Total sugars in grams")
    health_score: Optional[int] = Field(default=None, description="Nutrition Health Score (0-100)")
    food_type: Optional[str] = Field(default=None, description="Food group classification")
    dietary_tags: List[str] = Field(default_factory=list, description="Deterministically derived dietary tags (e.g., vegetarian, vegan, keto, paleo)")
    targeted_deficiency: Optional[str] = Field(default=None, description="Primary deficiency class targeted by this food/recipe")
    ranking_score: float = Field(default=0.0, description="Internal deterministic recommendation score (0-100)")
    recommendation_reason: str = Field(default="", description="Educational rationale for recommendation")

class RecipeSearchRequest(BaseModel):
    query: Optional[str] = Field(default=None, description="Search term for title or ingredients")
    category: Optional[str] = Field(default=None, description="Filter by food category")
    dietary_preference: str = Field(default="omnivore", description="Dietary preference filter (omnivore, vegetarian, vegan, keto, paleo)")
    allergies_intolerances: Union[List[str], str] = Field(default=[], description="List or comma-separated string of user allergies")
    prohibited_foods: Union[List[str], str] = Field(default=[], description="List or comma-separated string of excluded keywords")
    preferred_foods: Union[List[str], str] = Field(default=[], description="List or comma-separated string of preferred keywords")
    limit: int = Field(default=20, ge=1, le=100, description="Maximum number of recipe results")

class RecipeSearchResponse(BaseModel):
    recipes: List[Recipe] = Field(..., description="List of matching recipe/food candidates")
    total_count: int = Field(..., description="Total count of matching recipe/food candidates")
    disclaimer: str = Field(..., description="Educational disclaimer regarding nutrition suggestions")

class RecipeRecommendationRequest(BaseModel):
    predicted_class: str = Field(default="Healthy", description="Target deficiency class (Anemia, Scurvy, Rickets_Osteomalacia, Night_Blindness, Healthy)")
    risk_level: str = Field(default="Moderate Risk", description="Evaluated risk level string")
    risk_score: float = Field(default=50.0, ge=0.0, le=100.0, description="Evaluated risk score (0-100)")
    dietary_preference: str = Field(default="omnivore", description="Dietary preference filter")
    allergies_intolerances: Union[List[str], str] = Field(default=[], description="List or comma-separated string of user allergies")
    prohibited_foods: Union[List[str], str] = Field(default=[], description="List or comma-separated string of excluded keywords")
    preferred_foods: Union[List[str], str] = Field(default=[], description="List or comma-separated string of preferred keywords")
    limit: int = Field(default=20, ge=1, le=100, description="Maximum number of recipe recommendations")
