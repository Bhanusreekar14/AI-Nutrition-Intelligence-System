from fastapi import APIRouter, Depends, HTTPException, status
from app.core.security import get_current_user
from app.models.recommendation import DietRecommendationRequest
from app.models.meal import (
    WeeklyMealPlan,
    WeeklyMealPlanConstraints,
    MealReplacementRequest,
    MealReplacementResponse,
)
from app.services.meal_plan_generator import MealPlanGeneratorService
from app.services.meal_replacement import MealReplacementService
from pydantic import BaseModel, Field
from typing import Optional

router = APIRouter()

class GenerateMealPlanRequest(BaseModel):
    recommendation_request: DietRecommendationRequest = Field(
        default_factory=DietRecommendationRequest,
        description="Diet recommendation parameters including deficiency class, risk score, dietary preference, allergies, and prohibited/preferred foods"
    )
    weekly_constraints: Optional[WeeklyMealPlanConstraints] = Field(
        default=None,
        description="Optional weekly repetition and diversity constraints"
    )

@router.post(
    "/generate",
    response_model=WeeklyMealPlan,
    status_code=status.HTTP_200_OK,
    summary="Generate 7-Day Personalized Meal Plan",
    description=(
        "Generates a complete 7-day personalized meal plan (Days 1 to 7) with Breakfast, Lunch, "
        "Snack, and Dinner for each day, enforcing weekly repetition limits, consecutive-day diversity, "
        "and strict dietary and allergen safety filters."
    )
)
def generate_meal_plan(
    req_in: GenerateMealPlanRequest,
    current_user: dict = Depends(get_current_user)
) -> WeeklyMealPlan:
    try:
        return MealPlanGeneratorService.generate_7_day_plan(
            req=req_in.recommendation_request,
            weekly_constraints=req_in.weekly_constraints
        )
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid meal plan generation request: {str(ve)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate 7-day meal plan: {str(e)}"
        )

@router.post(
    "/replace",
    response_model=MealReplacementResponse,
    status_code=status.HTTP_200_OK,
    summary="Replace Meal Item in Existing Plan",
    description=(
        "Replaces a single target food item within a 7-day meal plan with a suitable alternative "
        "while enforcing dietary preferences, allergen safety, prohibited exclusions, and plan recalculation."
    )
)
def replace_meal_item(
    req_in: MealReplacementRequest,
    current_user: dict = Depends(get_current_user)
) -> MealReplacementResponse:
    try:
        return MealReplacementService.replace_food_in_plan(req_in)
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid meal replacement request: {str(ve)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to replace meal item: {str(e)}"
        )
