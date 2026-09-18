from fastapi import APIRouter, Depends, HTTPException, status
from app.core.security import get_current_user
from app.models.recommendation import DietRecommendationRequest, DietRecommendationResponse
from app.services.recommendation_service import RecommendationService

router = APIRouter()

@router.post(
    "",
    response_model=DietRecommendationResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Personalized Diet Recommendations",
    description=(
        "Generates rule-based personalized food and dietary recommendations matching predicted "
        "deficiency risks, user dietary preferences, and allergen restrictions based on USDA nutrition data. "
        "These food suggestions are for educational purposes and do not replace clinical medical nutrition therapy."
    )
)
def get_diet_recommendations(
    request_in: DietRecommendationRequest,
    current_user: dict = Depends(get_current_user)
) -> DietRecommendationResponse:
    try:
        return RecommendationService.get_recommendations(request_in)
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid recommendation request: {ve}"
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate personalized diet recommendations."
        )
