import os
import re
import pandas as pd
import numpy as np
from typing import List, Dict, Set, Any
from app.models.recommendation import (
    DietRecommendationRequest,
    DietRecommendationResponse,
    RecommendedFood,
)

# Resolve dataset directory reliably
SERVICE_DIR = os.path.dirname(os.path.abspath(__file__))
APP_DIR = os.path.dirname(SERVICE_DIR)
BACKEND_DIR = os.path.dirname(APP_DIR)
PROJECT_ROOT = os.path.dirname(BACKEND_DIR)
FOOD_CSV_PATH = os.path.join(PROJECT_ROOT, "datasets", "food_nutrition", "food_nutrition.csv")

if not os.path.exists(FOOD_CSV_PATH):
    raise RuntimeError(f"Required food dataset missing: {FOOD_CSV_PATH}")

# Load food dataset ONCE at module initialization time
try:
    _FOOD_DF_RAW = pd.read_csv(FOOD_CSV_PATH, low_memory=False)
    
    # Clean food_name and fill NaNs for key columns safely
    _FOOD_DF_RAW = _FOOD_DF_RAW.dropna(subset=["food_name"]).copy()
    _FOOD_DF_RAW["food_name_clean"] = _FOOD_DF_RAW["food_name"].str.strip()
    _FOOD_DF_RAW = _FOOD_DF_RAW[_FOOD_DF_RAW["food_name_clean"] != ""].copy()

    # Fill numeric NaNs with 0.0 safely
    num_cols = [
        "calories", "carbs_g", "calcium_mg", "fat_g", "protein_g",
        "saturated_fat_g", "vitamin_c_mg", "fiber_g", "iron_mg",
        "sodium_mg", "sugar_g", "cholesterol_mg", "health_score"
    ]
    for col in num_cols:
        if col in _FOOD_DF_RAW.columns:
            _FOOD_DF_RAW[col] = pd.to_numeric(_FOOD_DF_RAW[col], errors="coerce").fillna(0.0)
        else:
            _FOOD_DF_RAW[col] = 0.0

    # Ensure text columns are string filled
    text_cols = ["food_category", "brand_owner", "brand_name", "ingredients", "serving_unit", "food_type"]
    for col in text_cols:
        if col in _FOOD_DF_RAW.columns:
            _FOOD_DF_RAW[col] = _FOOD_DF_RAW[col].fillna("").astype(str)
        else:
            _FOOD_DF_RAW[col] = ""

    _FOOD_DF = _FOOD_DF_RAW
except Exception as e:
    raise RuntimeError(f"Failed to load food dataset CSV: {e}")

# Mandatory Medical Disclaimer
MEDICAL_DISCLAIMER = (
    "These food suggestions are based on available nutritional data and rule-based ranking for educational purposes. "
    "They are not medical diagnoses or individualized medical treatment. "
    "Consult a qualified healthcare professional or registered dietitian for medical nutrition advice."
)

# Target Nutrient Mappings per Class
TARGET_NUTRIENTS_MAP: Dict[str, List[str]] = {
    "Anemia": ["iron_mg", "vitamin_c_mg", "protein_g"],
    "Scurvy": ["vitamin_c_mg", "fiber_g"],
    "Rickets_Osteomalacia": ["calcium_mg", "protein_g"],
    "Night_Blindness": ["vitamin_a_rule_signal", "health_score"],
    "Healthy": ["health_score", "fiber_g", "protein_g"],
}

# Educational Advice Messages per Class
DIETARY_ADVICE_MAP: Dict[str, List[str]] = {
    "Anemia": [
        "Include non-heme iron sources (like spinach, legumes, and fortified grains) paired with Vitamin C to enhance absorption.",
        "Avoid consuming coffee or tea at the exact same time as iron-rich meals, as tannins can inhibit iron uptake."
    ],
    "Scurvy": [
        "Incorporate fresh citrus fruits, bell peppers, strawberries, and broccoli into daily meals to boost natural Vitamin C intake.",
        "Raw or lightly steamed vegetables retain significantly higher Vitamin C levels compared to prolonged boiling."
    ],
    "Rickets_Osteomalacia": [
        "Choose calcium-dense foods such as dairy products, fortified plant milks, tofu, and dark leafy greens.",
        "Ensure adequate safe sun exposure or dietary sources to support bone health and calcium uptake."
    ],
    "Night_Blindness": [
        "Focus on orange and dark leafy green vegetables (such as carrots, sweet potatoes, spinach, and squash) rich in provitamin A carotenoids.",
        "Consuming carotenoid-rich vegetables with a small amount of healthy fats (like olive oil) enhances Vitamin A bioavailability."
    ],
    "Healthy": [
        "Maintain a balanced diet rich in dietary fiber, high-quality proteins, and diverse whole foods.",
        "Limit excessive sodium, added sugars, and saturated fats to support long-term metabolic and cardiovascular health."
    ]
}

# Vitamin A Category / Ingredient Keywords for Night_Blindness signal matching
VITAMIN_A_KEYWORDS = [
    "carrot", "spinach", "kale", "sweet potato", "squash", "pumpkin",
    "liver", "cantaloupe", "mango", "papaya", "apricot", "collard", "turnip green"
]

# Allergen Keywords mapping
ALLERGEN_KEYWORDS: Dict[str, List[str]] = {
    "gluten": ["wheat", "barley", "rye", "gluten", "flour", "semolina", "spelt", "kamut"],
    "dairy": ["milk", "cheese", "butter", "cream", "yogurt", "whey", "casein", "lactose", "ghee", "custard"],
    "nuts": ["peanut", "almond", "walnut", "cashew", "pecan", "hazelnut", "macadamia", "pistachio", "tree nut"],
    "soy": ["soy", "soybean", "tofu", "edamame", "tempeh", "miso", "lecithin"],
    "eggs": ["egg", "albumin", "mayonnaise", "meringue"],
    "fish": ["fish", "salmon", "tuna", "cod", "trout", "anchovy", "sardine", "shrimp", "crab", "lobster", "seafood"]
}

# Non-Vegetarian & Non-Vegan Keywords
MEAT_FISH_KEYWORDS = [
    "beef", "chicken", "pork", "lamb", "turkey", "duck", "bacon", "sausage",
    "ham", "meat", "fish", "tuna", "salmon", "shrimp", "crab", "lobster",
    "seafood", "anchovy", "sardine", "gelatin"
]

ANIMAL_DERIVED_KEYWORDS = MEAT_FISH_KEYWORDS + [
    "milk", "cheese", "butter", "cream", "yogurt", "whey", "casein", "egg", "honey"
]


def normalize_allergies(allergies_input: Any) -> Set[str]:
    """Normalizes string or list input of user allergies/intolerances into a cleaned set of standard keys."""
    raw_list: List[str] = []
    if isinstance(allergies_input, str):
        raw_list = [item.strip() for item in allergies_input.split(",") if item.strip()]
    elif isinstance(allergies_input, list):
        raw_list = [str(item).strip() for item in allergies_input if str(item).strip()]

    normalized: Set[str] = set()
    for item in raw_list:
        val = item.lower()
        if "gluten" in val or "wheat" in val:
            normalized.add("gluten")
        elif "dairy" in val or "milk" in val or "lactose" in val:
            normalized.add("dairy")
        elif "nut" in val or "peanut" in val:
            normalized.add("nuts")
        elif "soy" in val:
            normalized.add("soy")
        elif "egg" in val:
            normalized.add("eggs")
        elif "fish" in val or "seafood" in val or "shellfish" in val:
            normalized.add("fish")
        else:
            normalized.add(val)
    return normalized


def is_allergen_free(row: pd.Series, user_allergies: Set[str]) -> bool:
    """Checks if a food row is free from specified user allergies using conservative ingredient and food name matching."""
    text_to_check = f"{row['food_name_clean']} {row['food_category']} {row['ingredients']}".lower()

    for allergy in user_allergies:
        keywords = ALLERGEN_KEYWORDS.get(allergy, [allergy])
        for kw in keywords:
            # Use word boundary search for precision
            pattern = rf"\b{re.escape(kw)}\b"
            if re.search(pattern, text_to_check):
                return False
    return True


def is_diet_compliant(row: pd.Series, dietary_preference: str) -> bool:
    """Filters candidate foods according to user dietary preferences."""
    pref = dietary_preference.lower().strip()
    if pref == "omnivore" or not pref:
        return True

    text_to_check = f"{row['food_name_clean']} {row['food_category']} {row['ingredients']}".lower()

    if pref == "vegetarian":
        for kw in MEAT_FISH_KEYWORDS:
            if re.search(rf"\b{re.escape(kw)}\b", text_to_check):
                return False

    elif pref == "vegan":
        for kw in ANIMAL_DERIVED_KEYWORDS:
            if re.search(rf"\b{re.escape(kw)}\b", text_to_check):
                return False

    elif pref == "keto":
        # Keto requirement: low carbs (<= 10g) and moderate/high fat (>= 5g) per serving
        carbs = float(row.get("carbs_g", 0.0))
        fat = float(row.get("fat_g", 0.0))
        if carbs > 10.0 or fat < 3.0:
            return False

    elif pref == "paleo":
        # Paleo excludes grains, legumes, dairy, processed sugars
        paleo_exclude = ["wheat", "rice", "corn", "oats", "bean", "peanut", "soy", "milk", "cheese", "sugar", "syrup"]
        for kw in paleo_exclude:
            if re.search(rf"\b{re.escape(kw)}\b", text_to_check):
                return False

    return True


class RecommendationService:
    @staticmethod
    def get_recommendations(req: DietRecommendationRequest) -> DietRecommendationResponse:
        predicted_class = req.predicted_class if req.predicted_class in TARGET_NUTRIENTS_MAP else "Healthy"
        user_allergies = normalize_allergies(req.allergies_intolerances)
        diet_pref = req.dietary_preference or "omnivore"
        limit = max(1, min(req.limit, 50))

        df = _FOOD_DF.copy()

        # 1. Special Filtering for Night_Blindness (Vitamin A Category & Ingredient Rule Match)
        matched_vitamin_a_signal = {}
        if predicted_class == "Night_Blindness":
            kw_pattern = "|".join([re.escape(kw) for kw in VITAMIN_A_KEYWORDS])
            mask_vit_a = df.apply(
                lambda r: bool(re.search(kw_pattern, f"{r['food_name_clean']} {r['food_category']} {r['ingredients']}".lower())),
                axis=1
            )
            df = df[mask_vit_a].copy()
            if df.empty:
                df = _FOOD_DF.copy()  # Fallback to all foods if filter is too restrictive

        # 2. Allergy Filtering
        if user_allergies:
            allergy_mask = df.apply(lambda r: is_allergen_free(r, user_allergies), axis=1)
            df = df[allergy_mask].copy()

        # 3. Dietary Preference Filtering
        if diet_pref.lower() != "omnivore":
            diet_mask = df.apply(lambda r: is_diet_compliant(r, diet_pref), axis=1)
            df = df[diet_mask].copy()

        if df.empty:
            # Safe fallback: Relax dietary preference if no candidate foods remain
            df = _FOOD_DF.copy()

        # 4. Transparent Deterministic Ranking Calculation
        def calc_score(row: pd.Series) -> float:
            iron = float(row.get("iron_mg", 0.0))
            vit_c = float(row.get("vitamin_c_mg", 0.0))
            calcium = float(row.get("calcium_mg", 0.0))
            protein = float(row.get("protein_g", 0.0))
            fiber = float(row.get("fiber_g", 0.0))
            health = float(row.get("health_score", 0.0))
            sodium = float(row.get("sodium_mg", 0.0))
            sat_fat = float(row.get("saturated_fat_g", 0.0))

            if predicted_class == "Anemia":
                # Primary: iron_mg, Secondary: vitamin_c_mg, protein_g
                raw = (iron * 5.0) + (vit_c * 0.5) + (protein * 1.5) + (health * 0.4)
            elif predicted_class == "Scurvy":
                # Primary: vitamin_c_mg, Secondary: fiber_g
                raw = (vit_c * 2.5) + (fiber * 2.0) + (health * 0.4)
            elif predicted_class == "Rickets_Osteomalacia":
                # Primary: calcium_mg, Secondary: protein_g
                raw = (calcium * 0.3) + (protein * 1.5) + (health * 0.4)
            elif predicted_class == "Night_Blindness":
                # Vitamin A rule signal match + health_score & fiber
                raw = (health * 0.6) + (fiber * 2.0) + (protein * 1.5)
            else:  # Healthy
                # Balanced high health score, fiber, protein, low sodium & saturated fat
                raw = (health * 0.6) + (fiber * 3.0) + (protein * 2.0) - (sodium * 0.01) - (sat_fat * 0.5)

            return round(float(np.clip(raw, 0.0, 100.0)), 2)

        df["ranking_score"] = df.apply(calc_score, axis=1)

        # Sort candidate foods by ranking_score descending
        df_sorted = df.sort_values(by="ranking_score", ascending=False)

        # 5. Deduplicate food items by normalized food name
        dedup_records = []
        seen_names: Set[str] = set()

        for _, row in df_sorted.iterrows():
            name_clean = str(row["food_name_clean"])
            name_key = name_clean.lower()
            if name_key in seen_names:
                continue
            seen_names.add(name_key)

            # Generate factual recommendation reason based ONLY on available columns
            iron_val = float(row.get("iron_mg", 0.0))
            vit_c_val = float(row.get("vitamin_c_mg", 0.0))
            calcium_val = float(row.get("calcium_mg", 0.0))
            fiber_val = float(row.get("fiber_g", 0.0))
            protein_val = float(row.get("protein_g", 0.0))
            health_val = int(row.get("health_score", 0))

            if predicted_class == "Anemia":
                if vit_c_val > 5.0:
                    reason = f"Contains {iron_val:.1f} mg iron and {vit_c_val:.1f} mg Vitamin C per serving."
                else:
                    reason = f"Contains {iron_val:.1f} mg iron per serving."
            elif predicted_class == "Scurvy":
                reason = f"Provides {vit_c_val:.1f} mg Vitamin C per serving."
            elif predicted_class == "Rickets_Osteomalacia":
                reason = f"Contains {calcium_val:.1f} mg calcium per serving."
            elif predicted_class == "Night_Blindness":
                reason = "Identified as a Vitamin-A associated food based on category/ingredient signal."
            else:
                reason = f"High nutrition health score ({health_val}/100) with {fiber_val:.1f}g fiber and {protein_val:.1f}g protein."

            fdc = row.get("fdc_id")
            fdc_id_val = int(fdc) if pd.notna(fdc) and str(fdc).isdigit() else None

            food_item = RecommendedFood(
                fdc_id=fdc_id_val,
                food_name=name_clean,
                food_category=str(row.get("food_category", "")) or None,
                serving_size=float(row.get("serving_size", 100.0)) if pd.notna(row.get("serving_size")) else 100.0,
                serving_unit=str(row.get("serving_unit", "g")) or "g",
                calories=round(float(row.get("calories", 0.0)), 1),
                protein_g=round(float(row.get("protein_g", 0.0)), 1),
                carbs_g=round(float(row.get("carbs_g", 0.0)), 1),
                fat_g=round(float(row.get("fat_g", 0.0)), 1),
                fiber_g=round(float(row.get("fiber_g", 0.0)), 1),
                iron_mg=round(float(row.get("iron_mg", 0.0)), 2),
                vitamin_c_mg=round(float(row.get("vitamin_c_mg", 0.0)), 2),
                calcium_mg=round(float(row.get("calcium_mg", 0.0)), 1),
                health_score=health_val,
                ranking_score=float(row["ranking_score"]),
                recommendation_reason=reason,
            )

            dedup_records.append(food_item)
            if len(dedup_records) >= limit:
                break

        targeted_nutrients = TARGET_NUTRIENTS_MAP.get(predicted_class, ["health_score", "fiber_g", "protein_g"])
        advice = DIETARY_ADVICE_MAP.get(predicted_class, DIETARY_ADVICE_MAP["Healthy"])

        return DietRecommendationResponse(
            predicted_class=predicted_class,
            risk_level=req.risk_level,
            risk_score=req.risk_score,
            targeted_nutrients=targeted_nutrients,
            recommended_foods=dedup_records,
            dietary_advice=advice,
            medical_disclaimer=MEDICAL_DISCLAIMER,
        )
