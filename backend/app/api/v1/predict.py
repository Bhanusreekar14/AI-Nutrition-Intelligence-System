from fastapi import APIRouter, Depends, HTTPException, status
from app.core.security import get_current_user
from app.models.prediction import DeficiencyPredictionRequest, DeficiencyPredictionResponse
from app.services.deficiency_prediction_service import DeficiencyPredictionService
from app.services.prediction_history_service import PredictionHistoryService

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
        res = DeficiencyPredictionService.predict(request_in)

        # Save historical snapshot with duplicate protection
        try:
            PredictionHistoryService.save_prediction_snapshot(
                user_id=current_user["user_id"],
                prediction=res,
                req_features=request_in
            )
        except Exception:
            pass

        return res
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
