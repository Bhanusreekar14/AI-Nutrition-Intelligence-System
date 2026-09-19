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

from app.services.deficiency_mapping import (
    get_deficiency_mapping,
    get_all_target_nutrients,
    DEFICIENCY_MAPPING_REGISTRY,
)

# Mandatory Medical Disclaimer
MEDICAL_DISCLAIMER = (
    "These food suggestions are based on available nutritional data and rule-based ranking for educational purposes. "
    "They are not medical diagnoses or individualized medical treatment. "
    "Consult a qualified healthcare professional or registered dietitian for medical nutrition advice."
)

# Backwards-compatible exports referencing the mapping registry
TARGET_NUTRIENTS_MAP: Dict[str, List[str]] = {
    cls_name: get_all_target_nutrients(cls_name)
    for cls_name in DEFICIENCY_MAPPING_REGISTRY.keys()
}

DIETARY_ADVICE_MAP: Dict[str, List[str]] = {
    cls_name: m.dietary_advice
    for cls_name, m in DEFICIENCY_MAPPING_REGISTRY.items()
}

VITAMIN_A_KEYWORDS = DEFICIENCY_MAPPING_REGISTRY["Night_Blindness"].signal_keywords


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


def normalize_string_or_list_input(input_val: Any) -> Set[str]:
    """Normalizes string (comma-separated) or list input into a cleaned set of lowercase terms."""
    raw_list: List[str] = []
    if isinstance(input_val, str):
        raw_list = [item.strip() for item in input_val.split(",") if item.strip()]
    elif isinstance(input_val, list):
        raw_list = [str(item).strip() for item in input_val if str(item).strip()]

    normalized: Set[str] = set()
    for item in raw_list:
        val = item.lower()
        if val:
            normalized.add(val)
    return normalized


def normalize_allergies(allergies_input: Any) -> Set[str]:
    """Normalizes string or list input of user allergies/intolerances into a cleaned set of standard keys."""
    raw_terms = normalize_string_or_list_input(allergies_input)
    normalized: Set[str] = set()
    for val in raw_terms:
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
            pattern = rf"\b{re.escape(kw)}"
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
        carbs = float(row.get("carbs_g", 0.0))
        fat = float(row.get("fat_g", 0.0))
        if carbs > 10.0 or fat < 3.0:
            return False

    elif pref == "paleo":
        paleo_exclude = ["wheat", "rice", "corn", "oats", "bean", "peanut", "soy", "milk", "cheese", "sugar", "syrup"]
        for kw in paleo_exclude:
            if re.search(rf"\b{re.escape(kw)}\b", text_to_check):
                return False

    return True


def is_prohibited_food(row: pd.Series, prohibited_terms: Set[str]) -> bool:
    """
    Centralized maintainable prohibited/exclusion check.
    Excludes foods if user-specified prohibited terms appear in name, category, or ingredients.
    Filtering happens BEFORE final ranking score calculation.
    """
    if not prohibited_terms:
        return False

    text_to_check = f"{row['food_name_clean']} {row['food_category']} {row['ingredients']}".lower()
    for term in prohibited_terms:
        if not term:
            continue
        # Check both word boundary and direct substring search for conservative exclusion
        pattern = rf"\b{re.escape(term)}\b"
        if re.search(pattern, text_to_check) or term in text_to_check:
            return True
    return False


class RecommendationService:
    @staticmethod
    def get_recommendations(req: DietRecommendationRequest) -> DietRecommendationResponse:
        predicted_class = req.predicted_class if req.predicted_class in TARGET_NUTRIENTS_MAP else "Healthy"
        user_allergies = normalize_allergies(req.allergies_intolerances)
        prohibited_terms = normalize_string_or_list_input(getattr(req, "prohibited_foods", []))
        preferred_terms = normalize_string_or_list_input(getattr(req, "preferred_foods", []))
        diet_pref = req.dietary_preference or "omnivore"
        limit = max(1, min(req.limit, 50))

        df = _FOOD_DF.copy()

        # 1. Candidate Selection & Deficiency Signal Pre-filtering (Night_Blindness)
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

        # 4. Centralized Prohibited Food Exclusions (BEFORE final ranking)
        if prohibited_terms:
            prohibited_mask = df.apply(lambda r: not is_prohibited_food(r, prohibited_terms), axis=1)
            df_filtered = df[prohibited_mask].copy()
            if not df_filtered.empty:
                df = df_filtered

        if df.empty:
            # Safe fallback if strict filters produce empty set
            df = _FOOD_DF.copy()

        # 5. Risk-Aware & Deficiency-Specific Deterministic Score Calculation
        # NOTE: ranking_score is an internal deterministic recommendation score (0-100), NOT a clinical or medical treatment score.
        risk_score_norm = float(np.clip(req.risk_score, 0.0, 100.0))
        # Higher risk score increases weighting of primary target nutrients
        risk_multiplier = 1.0 + (risk_score_norm / 100.0) * 0.75

        def calc_score(row: pd.Series) -> float:
            iron = float(row.get("iron_mg", 0.0))
            vit_c = float(row.get("vitamin_c_mg", 0.0))
            calcium = float(row.get("calcium_mg", 0.0))
            protein = float(row.get("protein_g", 0.0))
            fiber = float(row.get("fiber_g", 0.0))
            health = float(row.get("health_score", 0.0))
            sodium = float(row.get("sodium_mg", 0.0))
            sat_fat = float(row.get("saturated_fat_g", 0.0))

            text_lower = f"{row['food_name_clean']} {row['food_category']} {row['ingredients']}".lower()

            if predicted_class == "Anemia":
                # Primary: iron_mg (scaled by risk), Secondary: vitamin_c_mg, protein_g
                raw = (iron * 5.0 * risk_multiplier) + (vit_c * 0.5) + (protein * 1.5) + (health * 0.4)
            elif predicted_class == "Scurvy":
                # Primary: vitamin_c_mg (scaled by risk), Secondary: fiber_g
                raw = (vit_c * 2.5 * risk_multiplier) + (fiber * 2.0) + (health * 0.4)
            elif predicted_class == "Rickets_Osteomalacia":
                # Primary: calcium_mg (scaled by risk), Secondary: protein_g
                raw = (calcium * 0.3 * risk_multiplier) + (protein * 1.5) + (health * 0.4)
            elif predicted_class == "Night_Blindness":
                # Vitamin A rule signal count * risk multiplier + health & fiber
                kw_matches = sum(1 for kw in VITAMIN_A_KEYWORDS if kw in text_lower)
                raw = (kw_matches * 10.0 * risk_multiplier) + (health * 0.6) + (fiber * 2.0) + (protein * 1.5)
            else:  # Healthy
                # Balanced health score, fiber, protein, low sodium & saturated fat
                raw = (health * 0.6 * risk_multiplier) + (fiber * 3.0) + (protein * 2.0) - (sodium * 0.01) - (sat_fat * 0.5)

            # Optional user preference boost
            if preferred_terms:
                pref_boost = sum(5.0 for pref in preferred_terms if pref in text_lower)
                raw += min(pref_boost, 15.0)

            return round(float(np.clip(raw, 0.0, 100.0)), 2)

        df["ranking_score"] = df.apply(calc_score, axis=1)

        # Sort candidate foods by ranking_score descending
        df_sorted = df.sort_values(by="ranking_score", ascending=False)

        # 6. Deduplication, Diversity Enforcement & Alternative Food Selection
        dedup_records: List[RecommendedFood] = []
        seen_names: Set[str] = set()
        category_counts: Dict[str, int] = {}
        max_per_category = max(2, limit // 3)

        # First pass: collect diverse high-ranking foods across categories
        deferred_rows = []

        for _, row in df_sorted.iterrows():
            name_clean = str(row["food_name_clean"])
            name_key = name_clean.lower()
            if name_key in seen_names:
                continue

            category = str(row.get("food_category", "General")).strip() or "General"
            cat_count = category_counts.get(category, 0)

            if cat_count >= max_per_category and len(df_sorted) > limit * 2:
                deferred_rows.append(row)
                continue

            seen_names.add(name_key)
            category_counts[category] = cat_count + 1

            food_item = RecommendationService._build_recommended_food_object(row, predicted_class)
            dedup_records.append(food_item)
            if len(dedup_records) >= limit:
                break

        # Second pass: if category diversity restriction leaves room, fill remaining slots with deferred high-rank foods
        if len(dedup_records) < limit and deferred_rows:
            for row in deferred_rows:
                name_clean = str(row["food_name_clean"])
                name_key = name_clean.lower()
                if name_key in seen_names:
                    continue
                seen_names.add(name_key)
                food_item = RecommendationService._build_recommended_food_object(row, predicted_class)
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

    @staticmethod
    def _build_recommended_food_object(row: pd.Series, predicted_class: str) -> RecommendedFood:
        """Helper to construct factual, transparent RecommendedFood model instances."""
        name_clean = str(row["food_name_clean"])
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

        return RecommendedFood(
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
