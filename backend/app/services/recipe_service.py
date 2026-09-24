import os
import re
import pandas as pd
import numpy as np
from typing import List, Dict, Set, Optional, Any
from app.models.recipe import (
    Recipe,
    RecipeSearchRequest,
    RecipeSearchResponse,
    RecipeRecommendationRequest,
)
from app.services.recommendation_service import (
    _FOOD_DF,
    is_allergen_free,
    is_diet_compliant,
    is_prohibited_food,
    normalize_allergies,
    normalize_string_or_list_input,
    TARGET_NUTRIENTS_MAP,
    VITAMIN_A_KEYWORDS,
    MEDICAL_DISCLAIMER,
)

class RecipeService:
    @staticmethod
    def derive_dietary_tags(row: pd.Series) -> List[str]:
        """Deterministically derives dietary and allergen tags for a food record."""
        tags: List[str] = []

        # Dietary Preferences
        if is_diet_compliant(row, "vegetarian"):
            tags.append("vegetarian")
        if is_diet_compliant(row, "vegan"):
            tags.append("vegan")
        if is_diet_compliant(row, "keto"):
            tags.append("keto")
        if is_diet_compliant(row, "paleo"):
            tags.append("paleo")

        # Allergens
        if is_allergen_free(row, {"gluten"}):
            tags.append("gluten-free")
        if is_allergen_free(row, {"dairy"}):
            tags.append("dairy-free")
        if is_allergen_free(row, {"nuts"}):
            tags.append("nut-free")

        return tags

    @staticmethod
    def _build_recipe_object(
        row: pd.Series,
        predicted_class: Optional[str] = None,
        ranking_score: float = 0.0,
        recommendation_reason: str = ""
    ) -> Recipe:
        """Helper to construct factual Recipe model objects strictly from dataset fields."""
        fdc = row.get("fdc_id")
        fdc_id_val = int(fdc) if pd.notna(fdc) and str(fdc).isdigit() else None
        recipe_id = f"fdc_{fdc_id_val}" if fdc_id_val else f"rec_{hash(row['food_name_clean']) & 0xffffffff}"

        title = str(row["food_name_clean"])
        category = str(row.get("food_category", "")).strip() or None
        ingredients = str(row.get("ingredients", "")).strip() or None

        serving_size = float(row.get("serving_size", 0.0)) if pd.notna(row.get("serving_size")) and float(row.get("serving_size", 0.0)) > 0 else None
        serving_unit = str(row.get("serving_unit", "")).strip() or None

        calories = round(float(row.get("calories", 0.0)), 1) if pd.notna(row.get("calories")) else None
        protein_g = round(float(row.get("protein_g", 0.0)), 1) if pd.notna(row.get("protein_g")) else None
        carbs_g = round(float(row.get("carbs_g", 0.0)), 1) if pd.notna(row.get("carbs_g")) else None
        fat_g = round(float(row.get("fat_g", 0.0)), 1) if pd.notna(row.get("fat_g")) else None
        fiber_g = round(float(row.get("fiber_g", 0.0)), 1) if pd.notna(row.get("fiber_g")) else None

        iron_mg = round(float(row.get("iron_mg", 0.0)), 2) if pd.notna(row.get("iron_mg")) else None
        vitamin_c_mg = round(float(row.get("vitamin_c_mg", 0.0)), 2) if pd.notna(row.get("vitamin_c_mg")) else None
        calcium_mg = round(float(row.get("calcium_mg", 0.0)), 1) if pd.notna(row.get("calcium_mg")) else None
        sodium_mg = round(float(row.get("sodium_mg", 0.0)), 1) if pd.notna(row.get("sodium_mg")) else None
        sugar_g = round(float(row.get("sugar_g", 0.0)), 1) if pd.notna(row.get("sugar_g")) else None

        health_score_val = int(row.get("health_score", 0)) if pd.notna(row.get("health_score")) else None
        food_type = str(row.get("food_type", "")).strip() or None

        dietary_tags = RecipeService.derive_dietary_tags(row)

        return Recipe(
            recipe_id=recipe_id,
            fdc_id=fdc_id_val,
            title=title,
            category=category,
            ingredients=ingredients,
            serving_size=serving_size,
            serving_unit=serving_unit,
            calories=calories,
            protein_g=protein_g,
            carbs_g=carbs_g,
            fat_g=fat_g,
            fiber_g=fiber_g,
            iron_mg=iron_mg,
            vitamin_c_mg=vitamin_c_mg,
            calcium_mg=calcium_mg,
            sodium_mg=sodium_mg,
            sugar_g=sugar_g,
            health_score=health_score_val,
            food_type=food_type,
            dietary_tags=dietary_tags,
            targeted_deficiency=predicted_class,
            ranking_score=round(ranking_score, 2),
            recommendation_reason=recommendation_reason,
        )

    @staticmethod
    def search_recipes(req: RecipeSearchRequest) -> RecipeSearchResponse:
        """Searches and filters recipe/food candidates according to query terms, category, and strict safety rules."""
        df = _FOOD_DF.copy()

        user_allergies = normalize_allergies(req.allergies_intolerances)
        prohibited_terms = normalize_string_or_list_input(req.prohibited_foods)
        preferred_terms = normalize_string_or_list_input(req.preferred_foods)
        diet_pref = req.dietary_preference or "omnivore"
        limit = max(1, min(req.limit, 100))

        # 1. Mandatory Safety Order:
        # Step 1: Allergy Filtering
        if user_allergies:
            allergy_mask = df.apply(lambda r: is_allergen_free(r, user_allergies), axis=1)
            df = df[allergy_mask].copy()

        # Step 2: Dietary Preference Filtering
        if diet_pref.lower() != "omnivore":
            diet_mask = df.apply(lambda r: is_diet_compliant(r, diet_pref), axis=1)
            df = df[diet_mask].copy()

        # Step 3: Prohibited Food Filtering
        if prohibited_terms:
            prohibited_mask = df.apply(lambda r: not is_prohibited_food(r, prohibited_terms), axis=1)
            df = df[prohibited_mask].copy()

        # 2. Search Query Filtering (Title / Ingredients)
        if req.query and req.query.strip():
            q_clean = req.query.strip().lower()
            query_mask = df.apply(
                lambda r: q_clean in str(r["food_name_clean"]).lower() or q_clean in str(r.get("ingredients", "")).lower() or q_clean in str(r.get("food_category", "")).lower(),
                axis=1
            )
            df = df[query_mask].copy()

        # 3. Category Filtering
        if req.category and req.category.strip():
            cat_clean = req.category.strip().lower()
            cat_mask = df.apply(lambda r: cat_clean in str(r.get("food_category", "")).lower(), axis=1)
            df = df[cat_mask].copy()

        if df.empty:
            return RecipeSearchResponse(
                recipes=[],
                total_count=0,
                disclaimer=MEDICAL_DISCLAIMER
            )

        # 4. Preferred Food Boost & Scoring
        def calc_search_score(row: pd.Series) -> float:
            health = float(row.get("health_score", 0.0))
            score = health * 0.5
            text_lower = f"{row['food_name_clean']} {row['food_category']} {row['ingredients']}".lower()

            if preferred_terms:
                pref_boost = sum(10.0 for pref in preferred_terms if pref in text_lower)
                score += min(pref_boost, 30.0)

            return float(np.clip(score, 0.0, 100.0))

        df["search_score"] = df.apply(calc_search_score, axis=1)
        df_sorted = df.sort_values(by="search_score", ascending=False)

        # 5. Deduplication & Object Construction
        recipes: List[Recipe] = []
        seen_titles: Set[str] = set()

        for _, row in df_sorted.iterrows():
            title_clean = str(row["food_name_clean"]).strip().lower()
            if title_clean in seen_titles:
                continue
            seen_titles.add(title_clean)

            reason = "Matches your search criteria and dietary safety profile."
            recipe_obj = RecipeService._build_recipe_object(row, ranking_score=row["search_score"], recommendation_reason=reason)
            recipes.append(recipe_obj)
            if len(recipes) >= limit:
                break

        return RecipeSearchResponse(
            recipes=recipes,
            total_count=len(recipes),
            disclaimer=MEDICAL_DISCLAIMER
        )

    @staticmethod
    def get_recipe_by_id(recipe_id: str) -> Optional[Recipe]:
        """Retrieves a single recipe/food record by recipe_id or fdc_id."""
        if not recipe_id:
            return None

        clean_id = recipe_id.strip()
        df = _FOOD_DF

        # Case 1: fdc_12345 format
        if clean_id.startswith("fdc_"):
            try:
                fdc_val = int(clean_id.replace("fdc_", ""))
                match = df[df["fdc_id"] == fdc_val]
                if not match.empty:
                    return RecipeService._build_recipe_object(match.iloc[0], recommendation_reason="Single recipe record lookup.")
            except ValueError:
                pass

        # Case 2: Numeric string matching fdc_id directly
        if clean_id.isdigit():
            fdc_val = int(clean_id)
            match = df[df["fdc_id"] == fdc_val]
            if not match.empty:
                return RecipeService._build_recipe_object(match.iloc[0], recommendation_reason="Single recipe record lookup.")

        # Case 3: Match title
        q_lower = clean_id.lower()
        match = df[df["food_name_clean"].str.lower() == q_lower]
        if not match.empty:
            return RecipeService._build_recipe_object(match.iloc[0], recommendation_reason="Single recipe record lookup.")

        return None

    @staticmethod
    def get_recipe_recommendations(req: RecipeRecommendationRequest) -> RecipeSearchResponse:
        """Retrieves deficiency-targeted recipe recommendations matching dietary preferences and safety rules."""
        predicted_class = req.predicted_class if req.predicted_class in TARGET_NUTRIENTS_MAP else "Healthy"
        user_allergies = normalize_allergies(req.allergies_intolerances)
        prohibited_terms = normalize_string_or_list_input(req.prohibited_foods)
        preferred_terms = normalize_string_or_list_input(req.preferred_foods)
        diet_pref = req.dietary_preference or "omnivore"
        limit = max(1, min(req.limit, 100))

        df = _FOOD_DF.copy()

        # 1. Candidate Selection & Pre-filtering for Night_Blindness
        if predicted_class == "Night_Blindness":
            kw_pattern = "|".join([re.escape(kw) for kw in VITAMIN_A_KEYWORDS])
            mask_vit_a = df.apply(
                lambda r: bool(re.search(kw_pattern, f"{r['food_name_clean']} {r['food_category']} {r['ingredients']}".lower())),
                axis=1
            )
            df = df[mask_vit_a].copy()
            if df.empty:
                df = _FOOD_DF.copy()

        # 2. Strict Safety Order:
        # Step 1: Allergy Filtering
        if user_allergies:
            allergy_mask = df.apply(lambda r: is_allergen_free(r, user_allergies), axis=1)
            df = df[allergy_mask].copy()

        # Step 2: Dietary Preference Filtering
        if diet_pref.lower() != "omnivore":
            diet_mask = df.apply(lambda r: is_diet_compliant(r, diet_pref), axis=1)
            df = df[diet_mask].copy()

        # Step 3: Prohibited Food Exclusion
        if prohibited_terms:
            prohibited_mask = df.apply(lambda r: not is_prohibited_food(r, prohibited_terms), axis=1)
            df = df[prohibited_mask].copy()

        if df.empty:
            return RecipeSearchResponse(
                recipes=[],
                total_count=0,
                disclaimer=MEDICAL_DISCLAIMER
            )

        # 3. Deficiency-Aware Ranking Score Calculation (Reusing RecommendationService scoring logic)
        risk_score_norm = float(np.clip(req.risk_score, 0.0, 100.0))
        risk_multiplier = 1.0 + (risk_score_norm / 100.0) * 0.75

        def calc_recipe_score(row: pd.Series) -> float:
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
                raw = (iron * 5.0 * risk_multiplier) + (vit_c * 0.5) + (protein * 1.5) + (health * 0.4)
            elif predicted_class == "Scurvy":
                raw = (vit_c * 2.5 * risk_multiplier) + (fiber * 2.0) + (health * 0.4)
            elif predicted_class == "Rickets_Osteomalacia":
                raw = (calcium * 0.3 * risk_multiplier) + (protein * 1.5) + (health * 0.4)
            elif predicted_class == "Night_Blindness":
                kw_matches = sum(1 for kw in VITAMIN_A_KEYWORDS if kw in text_lower)
                raw = (kw_matches * 10.0 * risk_multiplier) + (health * 0.6) + (fiber * 2.0) + (protein * 1.5)
            else:  # Healthy
                raw = (health * 0.6 * risk_multiplier) + (fiber * 3.0) + (protein * 2.0) - (sodium * 0.01) - (sat_fat * 0.5)

            if preferred_terms:
                pref_boost = sum(5.0 for pref in preferred_terms if pref in text_lower)
                raw += min(pref_boost, 15.0)

            return round(float(np.clip(raw, 0.0, 100.0)), 2)

        df["ranking_score"] = df.apply(calc_recipe_score, axis=1)
        df_sorted = df.sort_values(by="ranking_score", ascending=False)

        # 4. Deduplication & Reasoning
        recipes: List[Recipe] = []
        seen_titles: Set[str] = set()

        for _, row in df_sorted.iterrows():
            title_clean = str(row["food_name_clean"]).strip().lower()
            if title_clean in seen_titles:
                continue
            seen_titles.add(title_clean)

            iron_val = float(row.get("iron_mg", 0.0))
            vit_c_val = float(row.get("vitamin_c_mg", 0.0))
            calcium_val = float(row.get("calcium_mg", 0.0))

            if predicted_class == "Anemia":
                reason = f"Recipe candidate provides {iron_val:.1f} mg iron and {vit_c_val:.1f} mg Vitamin C to support iron absorption."
            elif predicted_class == "Scurvy":
                reason = f"Recipe candidate provides {vit_c_val:.1f} mg Vitamin C per serving."
            elif predicted_class == "Rickets_Osteomalacia":
                reason = f"Recipe candidate provides {calcium_val:.1f} mg calcium per serving."
            elif predicted_class == "Night_Blindness":
                reason = "Identified as a Vitamin-A associated recipe based on ingredient/category signal."
            else:
                reason = f"Nutrient-dense recipe candidate with high health score ({int(row.get('health_score', 0))}/100)."

            recipe_obj = RecipeService._build_recipe_object(
                row,
                predicted_class=predicted_class,
                ranking_score=row["ranking_score"],
                recommendation_reason=reason
            )
            recipes.append(recipe_obj)
            if len(recipes) >= limit:
                break

        return RecipeSearchResponse(
            recipes=recipes,
            total_count=len(recipes),
            disclaimer=MEDICAL_DISCLAIMER
        )
