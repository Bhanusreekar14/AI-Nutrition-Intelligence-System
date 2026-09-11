from fastapi import APIRouter, Depends, HTTPException, status
from app.core.security import get_current_user
from app.models.prediction import DeficiencyPredictionRequest, DeficiencyPredictionResponse
from app.services.deficiency_prediction_service import DeficiencyPredictionService

router = APIRouter()

@router.post(
    "/predict",
    response_model=DeficiencyPredictionResponse,
    status_code=status.HTTP_200_OK,
    summary="Predict Nutritional Deficiency Risk",
    description=(
        "Exposes the trained XGBoost nutrition deficiency ML pipeline with SHAP feature attributions "
        "and application-level risk scores. These estimates are for research and educational purposes "
        "and do not replace clinical medical evaluation."
    )
)
def predict_deficiency_risk(
    request_in: DeficiencyPredictionRequest,
    current_user: dict = Depends(get_current_user)
) -> DeficiencyPredictionResponse:
    try:
        return DeficiencyPredictionService.predict(request_in)
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid prediction request features: {ve}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate deficiency risk prediction."
        )
