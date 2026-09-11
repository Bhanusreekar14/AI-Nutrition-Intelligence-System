from fastapi import APIRouter
from app.api.v1 import health, profile, diary, symptoms, blood_tests, food_search, predict

api_router = APIRouter()

api_router.include_router(health.router, tags=["Health Check"])
api_router.include_router(profile.router, prefix="/profile", tags=["Health Profile"])
api_router.include_router(diary.router, prefix="/diary", tags=["Food Diary"])
api_router.include_router(symptoms.router, prefix="/symptoms", tags=["Symptom Assessment"])
api_router.include_router(blood_tests.router, prefix="/blood-tests", tags=["Blood Test Results"])
api_router.include_router(food_search.router, prefix="/food", tags=["Food Search"])
api_router.include_router(predict.router, tags=["Deficiency Risk Prediction"])

