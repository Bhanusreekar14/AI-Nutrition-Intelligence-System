# pyrefly: ignore [missing-import]
from fastapi import APIRouter, Query, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
import httpx
from app.core.config import settings
from app.core.security import get_current_user

router = APIRouter()

class NormalizedFoodItem(BaseModel):
    id: str
    source: str
    externalId: str
    name: str
    servingSize: float
    servingUnit: str
    calories: float
    protein: float
    carbohydrates: float
    fat: float
    fiber: float
    sugar: float
    sodium: float
    vitaminD: float
    vitaminB12: float
    iron: float
    calcium: float

@router.get("/search", response_model=List[NormalizedFoodItem], summary="Search Foods via USDA & OpenFoodFacts")
async def search_foods(
    q: str = Query(..., min_length=1, description="Food name to search for"),
    current_user: dict = Depends(get_current_user)
):
    results: List[NormalizedFoodItem] = []
    
    # 1. Search USDA FoodData Central API
    try:
        usda_url = "https://api.nal.usda.gov/fdc/v1/foods/search"
        params = {
            "query": q,
            "pageSize": 10,
            "api_key": settings.USDA_API_KEY
        }
        async with httpx.AsyncClient(timeout=6.0) as client:
            resp = await client.get(usda_url, params=params)
            if resp.status_code == 200:
                data = resp.json()
                foods = data.get("foods", [])
                for f in foods:
                    fdc_id = str(f.get("fdcId", ""))
                    name = f.get("description", "Unknown Food")
                    serving_size = float(f.get("servingSize", 100.0) or 100.0)
                    serving_unit = str(f.get("servingSizeUnit", "g") or "g")
                    
                    nutrients = {n.get("nutrientName", "").lower(): float(n.get("value", 0.0) or 0.0) for n in f.get("foodNutrients", [])}
                    
                    # Extract nutrient values
                    cal = nutrients.get("energy", 0.0)
                    prot = nutrients.get("protein", 0.0)
                    carb = nutrients.get("carbohydrate, by difference", 0.0)
                    fat = nutrients.get("total lipid (fat)", 0.0)
                    fiber = nutrients.get("fiber, total dietary", 0.0)
                    sugar = nutrients.get("sugars, total including nlea", nutrients.get("total sugars", 0.0))
                    sod = nutrients.get("sodium, na", 0.0)
                    vit_d = nutrients.get("vitamin d (d2 + d3)", 0.0)
                    vit_b12 = nutrients.get("vitamin b-12", 0.0)
                    iron = nutrients.get("iron, fe", 0.0)
                    calc = nutrients.get("calcium, ca", 0.0)
                    
                    results.append(NormalizedFoodItem(
                        id=f"usda_{fdc_id}",
                        source="usda",
                        externalId=fdc_id,
                        name=name.title(),
                        servingSize=round(serving_size, 1),
                        servingUnit=serving_unit,
                        calories=round(cal, 1),
                        protein=round(prot, 1),
                        carbohydrates=round(carb, 1),
                        fat=round(fat, 1),
                        fiber=round(fiber, 1),
                        sugar=round(sugar, 1),
                        sodium=round(sod, 1),
                        vitaminD=round(vit_d, 2),
                        vitaminB12=round(vit_b12, 2),
                        iron=round(iron, 2),
                        calcium=round(calc, 2)
                    ))
    except Exception as e:
        print(f"USDA API error: {e}")

    # 2. Search OpenFoodFacts API if results are few or as fallback
    try:
        off_url = "https://world.openfoodfacts.org/cgi/search.pl"
        params = {
            "search_terms": q,
            "search_simple": "1",
            "action": "process",
            "json": "1",
            "page_size": 10
        }
        async with httpx.AsyncClient(timeout=6.0) as client:
            resp = await client.get(off_url, params=params)
            if resp.status_code == 200:
                data = resp.json()
                products = data.get("products", [])
                for p in products:
                    code = str(p.get("code", p.get("_id", "")))
                    name = p.get("product_name", p.get("product_name_en", "Unknown Product"))
                    if not name or name == "Unknown Product":
                        continue
                    
                    nutriments = p.get("nutriments", {})
                    cal = float(nutriments.get("energy-kcal_100g", nutriments.get("energy-kcal", 0.0)) or 0.0)
                    prot = float(nutriments.get("proteins_100g", 0.0) or 0.0)
                    carb = float(nutriments.get("carbohydrates_100g", 0.0) or 0.0)
                    fat = float(nutriments.get("fat_100g", 0.0) or 0.0)
                    fiber = float(nutriments.get("fiber_100g", 0.0) or 0.0)
                    sugar = float(nutriments.get("sugars_100g", 0.0) or 0.0)
                    sod = float(nutriments.get("sodium_100g", 0.0) or 0.0) * 1000  # g to mg
                    vit_d = float(nutriments.get("vitamin-d_100g", 0.0) or 0.0)
                    vit_b12 = float(nutriments.get("vitamin-b12_100g", 0.0) or 0.0)
                    iron = float(nutriments.get("iron_100g", 0.0) or 0.0)
                    calc = float(nutriments.get("calcium_100g", 0.0) or 0.0)
                    
                    results.append(NormalizedFoodItem(
                        id=f"off_{code}",
                        source="openfoodfacts",
                        externalId=code,
                        name=name.title(),
                        servingSize=100.0,
                        servingUnit="g",
                        calories=round(cal, 1),
                        protein=round(prot, 1),
                        carbohydrates=round(carb, 1),
                        fat=round(fat, 1),
                        fiber=round(fiber, 1),
                        sugar=round(sugar, 1),
                        sodium=round(sod, 1),
                        vitaminD=round(vit_d, 2),
                        vitaminB12=round(vit_b12, 2),
                        iron=round(iron, 2),
                        calcium=round(calc, 2)
                    ))
    except Exception as e:
        print(f"OpenFoodFacts API error: {e}")

    return results
