from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import Optional, List
from app.core.security import get_current_user
from app.models.recipe import (
    Recipe,
    RecipeSearchRequest,
    RecipeSearchResponse,
    RecipeRecommendationRequest,
)
from app.services.recipe_service import RecipeService

router = APIRouter()

@router.get(
    "/search",
    response_model=RecipeSearchResponse,
    status_code=status.HTTP_200_OK,
    summary="Search Recipes & Food Candidates",
    description="Search recipes and food candidates by query, category, dietary preferences, and safety filters."
)
def search_recipes(
    query: Optional[str] = Query(None, description="Search query string for title or ingredients"),
    category: Optional[str] = Query(None, description="Filter by food category"),
    dietary_preference: str = Query("omnivore", description="Dietary preference (omnivore, vegetarian, vegan, keto, paleo)"),
    allergies: Optional[List[str]] = Query(None, alias="allergies_intolerances", description="Allergies to exclude"),
    prohibited_foods: Optional[List[str]] = Query(None, description="Prohibited food keywords to exclude"),
    preferred_foods: Optional[List[str]] = Query(None, description="Preferred food keywords to boost"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of recipe items"),
    current_user: dict = Depends(get_current_user)
) -> RecipeSearchResponse:
    try:
        req = RecipeSearchRequest(
            query=query,
            category=category,
            dietary_preference=dietary_preference,
            allergies_intolerances=allergies or [],
            prohibited_foods=prohibited_foods or [],
            preferred_foods=preferred_foods or [],
            limit=limit
        )
        return RecipeService.search_recipes(req)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search recipes: {str(e)}"
        )

@router.get(
    "/{recipe_id}",
    response_model=Recipe,
    status_code=status.HTTP_200_OK,
    summary="Get Recipe Details by ID",
    description="Retrieves a single recipe or food candidate by its unique recipe_id or fdc_id."
)
def get_recipe_by_id(
    recipe_id: str,
    current_user: dict = Depends(get_current_user)
) -> Recipe:
    recipe = RecipeService.get_recipe_by_id(recipe_id)
    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recipe with ID '{recipe_id}' not found."
        )
    return recipe

@router.post(
    "/recommendations",
    response_model=RecipeSearchResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Deficiency-Targeted Recipe Recommendations",
    description="Generates deficiency-targeted recipe recommendations matching dietary profile and safety rules."
)
def get_recipe_recommendations(
    req: RecipeRecommendationRequest,
    current_user: dict = Depends(get_current_user)
) -> RecipeSearchResponse:
    try:
        return RecipeService.get_recipe_recommendations(req)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate recipe recommendations: {str(e)}"
        )
