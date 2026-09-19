import uuid
from typing import List, Dict, Set, Optional
from app.models.recommendation import (
    DietRecommendationRequest,
    RecommendedFood,
)
from app.models.meal import (
    MealType,
    MealSelectionConstraints,
    MealSelection,
    DailyMealPlan,
    WeeklyMealPlanConstraints,
    WeeklyMealPlan,
)
from app.services.recommendation_service import (
    RecommendationService,
    MEDICAL_DISCLAIMER,
)
from app.services.meal_selection import MealSelectionService

class MealPlanGeneratorService:
    @staticmethod
    def generate_7_day_plan(
        req: DietRecommendationRequest,
        weekly_constraints: Optional[WeeklyMealPlanConstraints] = None
    ) -> WeeklyMealPlan:
        """
        Generates a complete 7-day personalized meal plan (Days 1 to 7) with Breakfast,
        Lunch, Snack, and Dinner for each day, enforcing weekly repetition limits,
        consecutive-day diversity, and strict dietary/allergy safety filters.
        """
        if weekly_constraints is None:
            weekly_constraints = WeeklyMealPlanConstraints()

        daily_constraints = weekly_constraints.daily_constraints or MealSelectionConstraints()

        # Step 1: Fetch a comprehensive candidate pool of safe, ranked food recommendations.
        # We request a large candidate limit (50) to support 7-day diversity.
        candidate_req = req.model_copy(update={"limit": max(req.limit, 50)})
        recommendation_resp = RecommendationService.get_recommendations(candidate_req)
        candidate_pool: List[RecommendedFood] = recommendation_resp.recommended_foods

        weekly_food_counts: Dict[str, int] = {}
        weekly_category_counts: Dict[str, int] = {}
        prev_day_foods: Set[str] = set()

        daily_plans: List[DailyMealPlan] = []
        meal_order = [MealType.BREAKFAST, MealType.LUNCH, MealType.SNACK, MealType.DINNER]

        # Step 2: Loop through Day 1 to Day 7
        for day_num in range(1, 8):
            today_seen_foods: Set[str] = set()
            today_category_counts: Dict[str, int] = {}
            today_meals: Dict[MealType, MealSelection] = {}

            for meal_type in meal_order:
                target_count = daily_constraints.target_counts.get(meal_type, 2)
                selected_for_meal: List[RecommendedFood] = []

                # Rank candidates for this meal slot
                ranked_candidates = MealSelectionService._rank_candidates_for_meal(
                    candidate_pool=candidate_pool,
                    meal_type=meal_type,
                )

                # Pass 1: Strict Weekly Diversity
                # Pick foods not used today, not used yesterday (consecutive day limit),
                # and below max weekly repetition limit.
                for food in ranked_candidates:
                    if len(selected_for_meal) >= target_count:
                        break

                    name_clean = food.food_name.strip().lower()
                    cat = (food.food_category or "General").strip()

                    if name_clean in today_seen_foods:
                        continue
                    if name_clean in prev_day_foods and weekly_constraints.max_consecutive_day_repetition <= 1:
                        continue
                    if weekly_food_counts.get(name_clean, 0) >= weekly_constraints.max_weekly_food_repetition:
                        continue

                    selected_for_meal.append(food)
                    today_seen_foods.add(name_clean)
                    weekly_food_counts[name_clean] = weekly_food_counts.get(name_clean, 0) + 1
                    today_category_counts[cat] = today_category_counts.get(cat, 0) + 1
                    weekly_category_counts[cat] = weekly_category_counts.get(cat, 0) + 1

                # Pass 2: Relax consecutive day restriction if target count not met
                if len(selected_for_meal) < target_count:
                    for food in ranked_candidates:
                        if len(selected_for_meal) >= target_count:
                            break

                        name_clean = food.food_name.strip().lower()
                        cat = (food.food_category or "General").strip()

                        if name_clean in today_seen_foods:
                            continue
                        if weekly_food_counts.get(name_clean, 0) >= weekly_constraints.max_weekly_food_repetition:
                            continue

                        selected_for_meal.append(food)
                        today_seen_foods.add(name_clean)
                        weekly_food_counts[name_clean] = weekly_food_counts.get(name_clean, 0) + 1
                        today_category_counts[cat] = today_category_counts.get(cat, 0) + 1
                        weekly_category_counts[cat] = weekly_category_counts.get(cat, 0) + 1

                # Pass 3: Graceful fallback - if candidate pool is constrained by strict filters,
                # allow repeat items to ensure all 7 days have complete meals.
                if len(selected_for_meal) < target_count and candidate_pool:
                    for food in ranked_candidates:
                        if len(selected_for_meal) >= target_count:
                            break
                        name_clean = food.food_name.strip().lower()
                        if any(f.food_name.strip().lower() == name_clean for f in selected_for_meal):
                            continue

                        selected_for_meal.append(food)
                        today_seen_foods.add(name_clean)
                        weekly_food_counts[name_clean] = weekly_food_counts.get(name_clean, 0) + 1

                today_meals[meal_type] = MealSelection(
                    meal_type=meal_type,
                    target_count=target_count,
                    selected_foods=selected_for_meal,
                )

            # Update consecutive-day tracking for next day
            prev_day_foods = today_seen_foods.copy()

            # Aggregate daily totals
            d_cal = sum(f.calories or 0.0 for m in today_meals.values() for f in m.selected_foods)
            d_pro = sum(f.protein_g or 0.0 for m in today_meals.values() for f in m.selected_foods)
            d_carb = sum(f.carbs_g or 0.0 for m in today_meals.values() for f in m.selected_foods)
            d_fat = sum(f.fat_g or 0.0 for m in today_meals.values() for f in m.selected_foods)
            d_fib = sum(f.fiber_g or 0.0 for m in today_meals.values() for f in m.selected_foods)

            daily_plan = DailyMealPlan(
                day=day_num,
                meals=today_meals,
                total_calories=round(d_cal, 1),
                total_protein_g=round(d_pro, 1),
                total_carbs_g=round(d_carb, 1),
                total_fat_g=round(d_fat, 1),
                total_fiber_g=round(d_fib, 1),
                deficiency_class=recommendation_resp.predicted_class,
                medical_disclaimer=MEDICAL_DISCLAIMER,
            )
            daily_plans.append(daily_plan)

        # Step 3: Aggregate weekly totals across all 7 days
        total_w_cal = sum(d.total_calories for d in daily_plans)
        total_w_pro = sum(d.total_protein_g for d in daily_plans)
        total_w_carb = sum(d.total_carbs_g for d in daily_plans)
        total_w_fat = sum(d.total_fat_g for d in daily_plans)
        total_w_fib = sum(d.total_fiber_g for d in daily_plans)

        plan_id_str = f"plan_{req.predicted_class.lower()}_{uuid.uuid4().hex[:8]}"

        return WeeklyMealPlan(
            plan_id=plan_id_str,
            days=daily_plans,
            total_days=7,
            total_weekly_calories=round(total_w_cal, 1),
            total_weekly_protein_g=round(total_w_pro, 1),
            total_weekly_carbs_g=round(total_w_carb, 1),
            total_weekly_fat_g=round(total_w_fat, 1),
            total_weekly_fiber_g=round(total_w_fib, 1),
            deficiency_class=recommendation_resp.predicted_class,
            medical_disclaimer=MEDICAL_DISCLAIMER,
        )

    @staticmethod
    def generate_sample_7_day_plan(deficiency_class: str = "Anemia") -> WeeklyMealPlan:
        """Deterministic helper to generate a sample 7-day plan using existing food dataset records."""
        req = DietRecommendationRequest(
            predicted_class=deficiency_class,
            risk_level="Moderate Risk",
            risk_score=50.0,
            dietary_preference="omnivore",
            limit=50,
        )
        return MealPlanGeneratorService.generate_7_day_plan(req)
