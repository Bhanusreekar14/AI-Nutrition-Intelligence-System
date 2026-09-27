from fastapi import APIRouter, Depends, HTTPException, status, Query
from app.core.security import get_current_user
from app.services.prediction_history_service import PredictionHistoryService
from app.models.prediction_history import PredictionHistoryEntry, PredictionProgressResponse
from typing import List, Dict, Any

router = APIRouter()

@router.get(
    "/history",
    response_model=List[PredictionHistoryEntry],
    status_code=status.HTTP_200_OK,
    summary="Get Historical Deficiency Prediction Snapshots",
    description="Returns chronological prediction snapshots for the authenticated user over a 4, 8, or 12 week evaluation window."
)
def get_prediction_history(
    weeks: int = Query(4, description="Evaluation window in weeks: 4, 8, or 12"),
    current_user: dict = Depends(get_current_user)
) -> List[PredictionHistoryEntry]:
    if weeks not in (4, 8, 12):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid weeks parameter '{weeks}'. Supported evaluation windows are 4, 8, or 12 weeks."
        )

    try:
        raw_history = PredictionHistoryService.get_prediction_history(
            user_id=current_user["user_id"],
            weeks=weeks
        )
        return [PredictionHistoryEntry(**item) for item in raw_history]
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve prediction history: {str(e)}"
        )

@router.get(
    "/progress",
    response_model=PredictionProgressResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Longitudinal Health Progress Summary",
    description="Returns an aggregated deficiency risk progress summary, risk-level transitions, and symptom/biomarker trend data for 4, 8, or 12 weeks."
)
def get_prediction_progress(
    weeks: int = Query(4, description="Evaluation window in weeks: 4, 8, or 12"),
    current_user: dict = Depends(get_current_user)
) -> PredictionProgressResponse:
    if weeks not in (4, 8, 12):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid weeks parameter '{weeks}'. Supported evaluation windows are 4, 8, or 12 weeks."
        )

    try:
        res_dict = PredictionHistoryService.get_prediction_progress(
            user_id=current_user["user_id"],
            weeks=weeks
        )
        return PredictionProgressResponse(**res_dict)
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate prediction progress: {str(e)}"
        )
