import re
from typing import List, Dict, Set, Optional, Any
from app.models.recommendation import (
    DietRecommendationRequest,
    RecommendedFood,
)
from app.models.meal import (
    MealType,
    MealSelectionConstraints,
    MealSelection,
    DailyMealPlan,
)
from app.services.recommendation_service import (
    RecommendationService,
    MEDICAL_DISCLAIMER,
)

# Soft category/keyword affinity hints for realistic meal assignment
BREAKFAST_KEYWORDS = {"egg", "oats", "cereal", "pancake", "waffle", "toast", "bread", "fruit", "milk", "yogurt", "coffee", "tea", "juice", "breakfast"}
SNACK_KEYWORDS = {"fruit", "nut", "seed", "yogurt", "snack", "berry", "apple", "banana", "almond", "walnut", "bar", "cracker", "chip"}
LUNCH_DINNER_KEYWORDS = {"salad", "soup", "rice", "curry", "stew", "pasta", "chicken", "fish", "meat", "vegetable", "bean", "lentil", "grain", "sandwich"}

class MealSelectionService:
    @staticmethod
    def select_daily_meals(
        req: DietRecommendationRequest,
        constraints: Optional[MealSelectionConstraints] = None
    ) -> DailyMealPlan:
        """
        Generates a structured single-day meal plan (Breakfast, Lunch, Snack, Dinner)
        using deficiency-prioritized recommendation candidates while enforcing
        repetition limits, category diversity, and strict dietary/allergy filters.
        """
        if constraints is None:
            constraints = MealSelectionConstraints()

        # Step 1: Fetch a candidate pool of safe, ranked food recommendations.
        # We request a candidate limit of at least 30 to ensure sufficient diversity.
        candidate_req = req.model_copy(update={"limit": max(req.limit, 30)})
        recommendation_resp = RecommendationService.get_recommendations(candidate_req)
        candidate_pool: List[RecommendedFood] = recommendation_resp.recommended_foods

        # Step 2: Initialize daily tracking structures for repetition control
        seen_food_names: Set[str] = set()
        category_counts: Dict[str, int] = {}
        meals_dict: Dict[MealType, MealSelection] = {}

        # Define processing order for meals
        meal_order = [MealType.BREAKFAST, MealType.LUNCH, MealType.SNACK, MealType.DINNER]

        for meal_type in meal_order:
            target_count = constraints.target_counts.get(meal_type, 2)
            selected_foods_for_meal: List[RecommendedFood] = []

            # Filter & score candidates specifically for this meal slot
            candidates_for_meal = MealSelectionService._rank_candidates_for_meal(
                candidate_pool=candidate_pool,
                meal_type=meal_type,
            )

            # Pass 1: Select foods not yet used today and satisfying category repetition limit
            for food in candidates_for_meal:
                if len(selected_foods_for_meal) >= target_count:
                    break

                food_name_clean = food.food_name.strip().lower()
                category = (food.food_category or "General").strip()

                if food_name_clean in seen_food_names:
                    continue

                cat_count = category_counts.get(category, 0)
                if constraints.enforce_category_diversity and cat_count >= constraints.max_category_repetition_per_day:
                    continue

                # Select food
                selected_foods_for_meal.append(food)
                seen_food_names.add(food_name_clean)
                category_counts[category] = cat_count + 1

            # Pass 2: Relax category diversity constraint if target count not met, but keep unique foods
            if len(selected_foods_for_meal) < target_count:
                for food in candidates_for_meal:
                    if len(selected_foods_for_meal) >= target_count:
                        break

                    food_name_clean = food.food_name.strip().lower()
                    category = (food.food_category or "General").strip()

                    if food_name_clean in seen_food_names:
                        continue

                    selected_foods_for_meal.append(food)
                    seen_food_names.add(food_name_clean)
                    category_counts[category] = category_counts.get(category, 0) + 1

            # Pass 3: Graceful fallback - if dataset/candidate pool is too small to fulfill target count with 100% unique items,
            # fill remaining slots with top-ranked candidates to avoid leaving meal empty.
            if len(selected_foods_for_meal) < target_count and candidate_pool:
                for food in candidates_for_meal:
                    if len(selected_foods_for_meal) >= target_count:
                        break
                    # Avoid duplicate within the same single meal
                    if any(f.food_name.strip().lower() == food.food_name.strip().lower() for f in selected_foods_for_meal):
                        continue
                    selected_foods_for_meal.append(food)

            meals_dict[meal_type] = MealSelection(
                meal_type=meal_type,
                target_count=target_count,
                selected_foods=selected_foods_for_meal,
            )

        # Step 3: Aggregate nutritional totals across all assigned meals
        total_calories = 0.0
        total_protein = 0.0
        total_carbs = 0.0
        total_fat = 0.0
        total_fiber = 0.0

        for meal_sel in meals_dict.values():
            for food in meal_sel.selected_foods:
                total_calories += food.calories or 0.0
                total_protein += food.protein_g or 0.0
                total_carbs += food.carbs_g or 0.0
                total_fat += food.fat_g or 0.0
                total_fiber += food.fiber_g or 0.0

        return DailyMealPlan(
            day=1,
            meals=meals_dict,
            total_calories=round(total_calories, 1),
            total_protein_g=round(total_protein, 1),
            total_carbs_g=round(total_carbs, 1),
            total_fat_g=round(total_fat, 1),
            total_fiber_g=round(total_fiber, 1),
            deficiency_class=recommendation_resp.predicted_class,
            medical_disclaimer=MEDICAL_DISCLAIMER,
        )

    @staticmethod
    def _rank_candidates_for_meal(
        candidate_pool: List[RecommendedFood],
        meal_type: MealType,
    ) -> List[RecommendedFood]:
        """
        Ranks candidate foods for a specific meal slot, maintaining primary deficiency
        ranking scores while applying secondary meal-affinity adjustments.
        """
        def compute_meal_suitability_score(food: RecommendedFood) -> float:
            text = f"{food.food_name} {food.food_category or ''}".lower()
            affinity_boost = 0.0

            if meal_type == MealType.BREAKFAST:
                if any(kw in text for kw in BREAKFAST_KEYWORDS):
                    affinity_boost += 5.0
            elif meal_type == MealType.SNACK:
                if any(kw in text for kw in SNACK_KEYWORDS):
                    affinity_boost += 5.0
            elif meal_type in (MealType.LUNCH, MealType.DINNER):
                if any(kw in text for kw in LUNCH_DINNER_KEYWORDS):
                    affinity_boost += 3.0

            # Base ranking_score carries 90% weight; affinity boost carries secondary weight
            return food.ranking_score + affinity_boost

        return sorted(candidate_pool, key=compute_meal_suitability_score, reverse=True)
