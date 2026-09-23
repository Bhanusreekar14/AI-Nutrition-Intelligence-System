import copy
from typing import List, Dict, Set, Optional, Tuple
from app.models.recommendation import (
    DietRecommendationRequest,
    RecommendedFood,
)
from app.models.meal import (
    MealType,
    MealSelection,
    DailyMealPlan,
    WeeklyMealPlan,
    MealReplacementRequest,
    MealReplacementResponse,
)
from app.services.recommendation_service import (
    RecommendationService,
    MEDICAL_DISCLAIMER,
)
from app.services.meal_selection import MealSelectionService


class MealReplacementService:
    @staticmethod
    def replace_food_in_plan(req: MealReplacementRequest) -> MealReplacementResponse:
        """
        Replaces a single food item in an existing 7-day meal plan with a safety-filtered,
        deficiency-aware alternative while maintaining strict plan immutability for all
        unrequested items, meals, and days.
        """
        weekly_plan = req.weekly_plan
        target_day_num = req.day
        target_meal_type = req.meal_type
        target_food_name_clean = req.target_food_name.strip().lower()

        # Step 1: Locate target day
        target_day_idx: Optional[int] = None
        target_day: Optional[DailyMealPlan] = None

        for idx, day in enumerate(weekly_plan.days):
            if day.day == target_day_num:
                target_day_idx = idx
                target_day = day
                break

        if target_day is None or target_day_idx is None:
            raise ValueError(f"Day {target_day_num} not found in the provided weekly meal plan.")

        # Step 2: Locate target meal slot
        if target_meal_type not in target_day.meals:
            raise ValueError(f"Meal slot '{target_meal_type.value}' not found on day {target_day_num}.")

        target_meal = target_day.meals[target_meal_type]

        # Step 3: Locate target food item within the meal
        original_food_idx: Optional[int] = None
        original_food: Optional[RecommendedFood] = None

        for idx, food in enumerate(target_meal.selected_foods):
            if food.food_name.strip().lower() == target_food_name_clean:
                original_food_idx = idx
                original_food = food
                break

        # Fallback substring match if exact match not found
        if original_food is None:
            for idx, food in enumerate(target_meal.selected_foods):
                if target_food_name_clean in food.food_name.strip().lower():
                    original_food_idx = idx
                    original_food = food
                    break

        if original_food is None or original_food_idx is None:
            raise ValueError(
                f"Food item '{req.target_food_name}' not found in {target_meal_type.value} on day {target_day_num}."
            )

        # Step 4: Collect existing foods in the plan for avoidance
        orig_name_clean = original_food.food_name.strip().lower()

        today_used_names: Set[str] = set()
        for m in target_day.meals.values():
            for f in m.selected_foods:
                today_used_names.add(f.food_name.strip().lower())

        weekly_used_names: Set[str] = set()
        for d in weekly_plan.days:
            for m in d.meals.values():
                for f in m.selected_foods:
                    weekly_used_names.add(f.food_name.strip().lower())

        # Step 5: Fetch safety-filtered candidates using RecommendationService
        predicted_class = req.predicted_class or weekly_plan.deficiency_class or "Healthy"
        rec_req = DietRecommendationRequest(
            predicted_class=predicted_class,
            risk_level=req.risk_level,
            risk_score=req.risk_score,
            dietary_preference=req.dietary_preference,
            allergies_intolerances=req.allergies_intolerances,
            prohibited_foods=req.prohibited_foods,
            preferred_foods=req.preferred_foods,
            limit=50,
        )

        rec_response = RecommendationService.get_recommendations(rec_req)
        raw_candidates = rec_response.recommended_foods

        # Filter out the original item strictly
        valid_candidates = [
            f for f in raw_candidates if f.food_name.strip().lower() != orig_name_clean
        ]

        if not valid_candidates:
            raise ValueError("No safe replacement candidate available matching all safety and dietary constraints.")

        # Rank candidates for suitability in the target meal slot
        ranked_candidates = MealSelectionService._rank_candidates_for_meal(
            candidate_pool=valid_candidates,
            meal_type=target_meal_type,
        )

        # Step 6: Select best replacement candidate
        replacement_food: Optional[RecommendedFood] = None
        is_fallback = False

        # Pass 1: Select top candidate not used in the target day
        for food in ranked_candidates:
            f_name_clean = food.food_name.strip().lower()
            if f_name_clean not in today_used_names:
                replacement_food = food
                is_fallback = False
                break

        # Pass 2: Select top candidate not used in the target meal (allows day-repetition if needed)
        if replacement_food is None:
            target_meal_food_names = {f.food_name.strip().lower() for f in target_meal.selected_foods if f.food_name.strip().lower() != orig_name_clean}
            for food in ranked_candidates:
                f_name_clean = food.food_name.strip().lower()
                if f_name_clean not in target_meal_food_names:
                    replacement_food = food
                    is_fallback = True
                    break

        # Pass 3: Fallback to top ranked valid candidate
        if replacement_food is None and ranked_candidates:
            replacement_food = ranked_candidates[0]
            is_fallback = True

        if replacement_food is None:
            raise ValueError("No safe replacement candidate available matching all safety and dietary constraints.")

        # Step 7: Perform Single-Item Replacement & Maintain Plan Immutability
        # Deep copy the weekly plan to ensure original objects are not mutated in-place
        updated_weekly_plan_dict = weekly_plan.model_dump()

        # Update selected food in target meal
        day_dict = updated_weekly_plan_dict["days"][target_day_idx]
        meal_dict = day_dict["meals"][target_meal_type.value]
        meal_dict["selected_foods"][original_food_idx] = replacement_food.model_dump()

        # Recalculate target day totals
        day_meals = day_dict["meals"]
        d_cal = sum(f["calories"] or 0.0 for m in day_meals.values() for f in m["selected_foods"])
        d_pro = sum(f["protein_g"] or 0.0 for m in day_meals.values() for f in m["selected_foods"])
        d_carb = sum(f["carbs_g"] or 0.0 for m in day_meals.values() for f in m["selected_foods"])
        d_fat = sum(f["fat_g"] or 0.0 for m in day_meals.values() for f in m["selected_foods"])
        d_fib = sum(f["fiber_g"] or 0.0 for m in day_meals.values() for f in m["selected_foods"])

        day_dict["total_calories"] = round(d_cal, 1)
        day_dict["total_protein_g"] = round(d_pro, 1)
        day_dict["total_carbs_g"] = round(d_carb, 1)
        day_dict["total_fat_g"] = round(d_fat, 1)
        day_dict["total_fiber_g"] = round(d_fib, 1)

        # Recalculate weekly totals
        all_days = updated_weekly_plan_dict["days"]
        w_cal = sum(d["total_calories"] for d in all_days)
        w_pro = sum(d["total_protein_g"] for d in all_days)
        w_carb = sum(d["total_carbs_g"] for d in all_days)
        w_fat = sum(d["total_fat_g"] for d in all_days)
        w_fib = sum(d["total_fiber_g"] for d in all_days)

        updated_weekly_plan_dict["total_weekly_calories"] = round(w_cal, 1)
        updated_weekly_plan_dict["total_weekly_protein_g"] = round(w_pro, 1)
        updated_weekly_plan_dict["total_weekly_carbs_g"] = round(w_carb, 1)
        updated_weekly_plan_dict["total_weekly_fat_g"] = round(w_fat, 1)
        updated_weekly_plan_dict["total_weekly_fiber_g"] = round(w_fib, 1)

        # Reconstruct updated Pydantic models
        updated_weekly_plan = WeeklyMealPlan.model_validate(updated_weekly_plan_dict)
        updated_day = updated_weekly_plan.days[target_day_idx]
        updated_meal = updated_day.meals[target_meal_type]

        # Generate replacement explanation
        fallback_note = " (Selected via fallback constraints)" if is_fallback else ""
        reason = (
            f"Replaced '{original_food.food_name}' with '{replacement_food.food_name}' "
            f"in {target_meal_type.value} on Day {target_day_num} to fit user preferences "
            f"and deficiency profile ({predicted_class}){fallback_note}."
        )

        return MealReplacementResponse(
            original_food=original_food,
            replacement_food=replacement_food,
            replacement_reason=reason,
            is_fallback=is_fallback,
            updated_meal=updated_meal,
            updated_day=updated_day,
            updated_weekly_plan=updated_weekly_plan,
            medical_disclaimer=MEDICAL_DISCLAIMER,
        )
