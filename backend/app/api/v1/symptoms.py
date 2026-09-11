from fastapi import APIRouter, Depends, HTTPException, status, Query
from app.core.security import get_current_user
from app.models.symptoms import SymptomAssessmentCreate, SymptomAssessmentResponse
from app.db.supabase import get_supabase_admin_client
from typing import List, Optional
from datetime import date

router = APIRouter()

@router.get("", response_model=List[SymptomAssessmentResponse], summary="Get User Symptom Assessments")
def get_symptom_assessments(
    assessment_date: Optional[date] = Query(None, description="Filter by date (YYYY-MM-DD)"),
    current_user: dict = Depends(get_current_user)
):
    supabase = get_supabase_admin_client()
    query = supabase.table("symptom_assessments").select("*").eq("user_id", current_user["user_id"])
    if assessment_date:
        query = query.eq("assessment_date", str(assessment_date))
    res = query.order("assessment_date", desc=True).execute()
    return res.data or []

@router.post("", response_model=List[SymptomAssessmentResponse], status_code=status.HTTP_201_CREATED, summary="Record Symptom Assessment")
def create_symptom_assessment(
    payload_in: SymptomAssessmentCreate,
    current_user: dict = Depends(get_current_user)
):
    supabase = get_supabase_admin_client()
    user_id = current_user["user_id"]
    assessment_date_str = str(payload_in.assessment_date)
    
    records = []
    for item in payload_in.assessments:
        records.append({
            "user_id": user_id,
            "symptom": item.symptom,
            "severity": item.severity,
            "assessment_date": assessment_date_str,
        })
        
    if not records:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No symptoms provided.")
        
    res = supabase.table("symptom_assessments").insert(records).execute()
    return res.data or []
