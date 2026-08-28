from fastapi import APIRouter
from app.api.v1 import health, profile, diary

api_router = APIRouter()

api_router.include_router(health.router, tags=["Health Check"])
api_router.include_router(profile.router, prefix="/profile", tags=["Health Profile"])
api_router.include_router(diary.router, prefix="/diary", tags=["Food Diary"])
