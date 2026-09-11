from fastapi import APIRouter, Depends, HTTPException, status, Query
from app.core.security import get_current_user
from app.models.blood_tests import BloodTestCreate, BloodTestUpdate, BloodTestResponse
from app.db.supabase import get_supabase_admin_client
from typing import List, Optional

router = APIRouter()

@router.get("", response_model=List[BloodTestResponse], summary="Get User Blood Test Entries")
def get_blood_tests(current_user: dict = Depends(get_current_user)):
    supabase = get_supabase_admin_client()
    res = supabase.table("blood_test_results").select("*").eq("user_id", current_user["user_id"]).order("test_date", desc=True).execute()
    return res.data or []

@router.post("", response_model=BloodTestResponse, status_code=status.HTTP_201_CREATED, summary="Create Blood Test Entry")
def create_blood_test(
    test_in: BloodTestCreate,
    current_user: dict = Depends(get_current_user)
):
    supabase = get_supabase_admin_client()
    payload = test_in.model_dump()
    payload["user_id"] = current_user["user_id"]
    payload["test_date"] = str(payload["test_date"])
    
    res = supabase.table("blood_test_results").insert(payload).execute()
    if not res.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to record blood test entry."
        )
    return res.data[0]

@router.put("/{test_id}", response_model=BloodTestResponse, summary="Update Blood Test Entry")
def update_blood_test(
    test_id: str,
    test_in: BloodTestUpdate,
    current_user: dict = Depends(get_current_user)
):
    supabase = get_supabase_admin_client()
    payload = test_in.model_dump(exclude_unset=True)
    if "test_date" in payload and payload["test_date"]:
        payload["test_date"] = str(payload["test_date"])
        
    res = supabase.table("blood_test_results").update(payload).eq("id", test_id).eq("user_id", current_user["user_id"]).execute()
    if not res.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blood test record not found or unauthorized."
        )
    return res.data[0]
