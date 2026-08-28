from fastapi import APIRouter, Depends, HTTPException, status, Query
from app.core.security import get_current_user
from app.models.diary import FoodDiaryCreate, FoodDiaryResponse, DailyNutritionSummary
from app.db.supabase import get_supabase_admin_client
from typing import List, Optional
from datetime import date

router = APIRouter()

@router.get("", response_model=List[FoodDiaryResponse], summary="Get User Food Diary Entries")
def get_diary_entries(
    logged_date: Optional[date] = Query(None, description="Filter by date (YYYY-MM-DD)"),
    current_user: dict = Depends(get_current_user)
):
    supabase = get_supabase_admin_client()
    query = supabase.table("food_diary").select("*").eq("user_id", current_user["user_id"])
    
    if logged_date:
        query = query.eq("logged_date", str(logged_date))
        
    res = query.order("created_at", desc=False).execute()
    return res.data or []

@router.post("", response_model=FoodDiaryResponse, status_code=status.HTTP_201_CREATED, summary="Create Food Diary Entry")
def create_diary_entry(
    entry_in: FoodDiaryCreate,
    current_user: dict = Depends(get_current_user)
):
    supabase = get_supabase_admin_client()
    payload = entry_in.model_dump()
    payload["user_id"] = current_user["user_id"]
    payload["logged_date"] = str(payload["logged_date"])
    
    res = supabase.table("food_diary").insert(payload).execute()
    if not res.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to insert food diary entry."
        )
    return res.data[0]

@router.delete("/{entry_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete Food Diary Entry")
def delete_diary_entry(
    entry_id: str,
    current_user: dict = Depends(get_current_user)
):
    supabase = get_supabase_admin_client()
    res = supabase.table("food_diary").delete().eq("id", entry_id).eq("user_id", current_user["user_id"]).execute()
    return None

@router.get("/summary", response_model=DailyNutritionSummary, summary="Get Daily Nutrition Summary")
def get_daily_summary(
    logged_date: date = Query(..., description="Date for summary (YYYY-MM-DD)"),
    current_user: dict = Depends(get_current_user)
):
    supabase = get_supabase_admin_client()
    res = supabase.table("food_diary").select("*").eq("user_id", current_user["user_id"]).eq("logged_date", str(logged_date)).execute()
    
    entries = res.data or []
    total_calories = sum(e.get("calories", 0) for e in entries)
    total_protein = sum(e.get("protein_g", 0) for e in entries)
    total_carbs = sum(e.get("carbs_g", 0) for e in entries)
    total_fat = sum(e.get("fat_g", 0) for e in entries)
    
    return DailyNutritionSummary(
        logged_date=logged_date,
        total_calories=round(total_calories, 2),
        total_protein_g=round(total_protein, 2),
        total_carbs_g=round(total_carbs, 2),
        total_fat_g=round(total_fat, 2),
        entry_count=len(entries)
    )
