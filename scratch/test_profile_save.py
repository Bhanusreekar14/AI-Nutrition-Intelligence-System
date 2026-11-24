import sys
import os

sys.path.insert(0, os.path.abspath("backend"))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

AUTH_HEADER = {
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIwMDAwMDAwMC0wMDAwLTAwMDAtMDAwMC0wMDAwMDAwMDAwMDEiLCJlbWFpbCI6InVzZXJAZXhhbXBsZS5jb20iLCJyb2xlIjoiYXV0aGVudGljYXRlZCJ9.dummy_signature"
}

payload = {
    "age": 30,
    "gender": "male",
    "height_cm": 175.0,
    "weight_kg": 75.0,
    "activity_level": "moderately_active",
    "dietary_preference": "balanced",
    "allergies_intolerances": ["lactose"],
    "health_goals": ["maintain_weight"]
}

print("Testing POST /api/v1/profile ...")
res_post = client.post("/api/v1/profile", json=payload, headers=AUTH_HEADER)
print("POST status:", res_post.status_code)
print("POST response:", res_post.json())

assert res_post.status_code == 201, f"Expected 201, got {res_post.status_code}"

print("\nTesting GET /api/v1/profile/me ...")
res_get = client.get("/api/v1/profile/me", headers=AUTH_HEADER)
print("GET status:", res_get.status_code)
print("GET response:", res_get.json())

assert res_get.status_code == 200, f"Expected 200, got {res_get.status_code}"

print("\nSUCCESS: Profile endpoints work perfectly!")
