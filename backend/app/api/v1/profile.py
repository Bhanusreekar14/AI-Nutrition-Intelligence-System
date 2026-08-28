from fastapi import APIRouter, Depends, HTTPException, status
from app.core.security import get_current_user
from app.models.profile import HealthProfileCreate, HealthProfileResponse, HealthProfileUpdate
from app.db.supabase import get_supabase_admin_client
from typing import Optional

router = APIRouter()

def calculate_bmr_tdee(profile: dict) -> tuple[float, float]:
    """
    Calculates BMR using Mifflin-St Jeor Equation and TDEE based on activity level.
    """
    weight = profile["weight_kg"]
    height = profile["height_cm"]
    age = profile["age"]
    gender = profile["gender"]
    
    # BMR Calculation (Mifflin-St Jeor)
    if gender == "male":
        bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5
    elif gender == "female":
        bmr = (10 * weight) + (6.25 * height) - (5 * age) - 161
    else:
        # Neutral average
        bmr = (10 * weight) + (6.25 * height) - (5 * age) - 78
        
    activity_multipliers = {
        "sedentary": 1.2,
        "lightly_active": 1.375,
        "moderately_active": 1.55,
        "very_active": 1.725,
        "extra_active": 1.9
    }
    multiplier = activity_multipliers.get(profile.get("activity_level", "sedentary"), 1.2)
    tdee = bmr * multiplier
    return round(bmr, 2), round(tdee, 2)

@router.get("/me", response_model=HealthProfileResponse, summary="Get Current User Health Profile")
def get_my_health_profile(current_user: dict = Depends(get_current_user)):
    supabase = get_supabase_admin_client()
    res = supabase.table("health_profiles").select("*").eq("user_id", current_user["user_id"]).execute()
    
    if not res.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Health profile not found for current user."
        )
    
    profile_data = res.data[0]
    bmr, tdee = calculate_bmr_tdee(profile_data)
    profile_data["bmr"] = bmr
    profile_data["tdee"] = tdee
    return profile_data

@router.post("", response_model=HealthProfileResponse, status_code=status.HTTP_201_CREATED, summary="Create or Update Health Profile")
def upsert_health_profile(
    profile_in: HealthProfileCreate,
    current_user: dict = Depends(get_current_user)
):
    supabase = get_supabase_admin_client()
    user_id = current_user["user_id"]
    
    payload = profile_in.model_dump()
    payload["user_id"] = user_id
    
    # Check existing profile
    res = supabase.table("health_profiles").select("id").eq("user_id", user_id).execute()
    
    if res.data:
        # Update existing
        profile_id = res.data[0]["id"]
        update_res = supabase.table("health_profiles").update(payload).eq("id", profile_id).execute()
        saved_profile = update_res.data[0]
    else:
        # Insert new
        insert_res = supabase.table("health_profiles").insert(payload).execute()
        saved_profile = insert_res.data[0]
        
    bmr, tdee = calculate_bmr_tdee(saved_profile)
    saved_profile["bmr"] = bmr
    saved_profile["tdee"] = tdee
    return saved_profile
