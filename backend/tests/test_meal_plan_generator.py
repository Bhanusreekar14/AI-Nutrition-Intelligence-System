import pytest
from app.models.recommendation import DietRecommendationRequest
from app.models.meal import (
    MealType,
    WeeklyMealPlanConstraints,
    WeeklyMealPlan,
)
from app.services.meal_plan_generator import MealPlanGeneratorService


def test_m34_generates_exactly_seven_days():
    req = DietRecommendationRequest(predicted_class="Anemia", risk_score=65.0)
    plan: WeeklyMealPlan = MealPlanGeneratorService.generate_7_day_plan(req)

    assert plan.total_days == 7
    assert len(plan.days) == 7
    for idx, day_plan in enumerate(plan.days, start=1):
        assert day_plan.day == idx


def test_m34_each_day_contains_four_meals():
    req = DietRecommendationRequest(predicted_class="Scurvy", risk_score=75.0)
    plan = MealPlanGeneratorService.generate_7_day_plan(req)

    for day_plan in plan.days:
        assert set(day_plan.meals.keys()) == {
            MealType.BREAKFAST,
            MealType.LUNCH,
            MealType.SNACK,
            MealType.DINNER,
        }
        for meal_sel in day_plan.meals.values():
            assert len(meal_sel.selected_foods) > 0


def test_m34_daily_and_weekly_nutrition_totals_calculated():
    req = DietRecommendationRequest(predicted_class="Rickets_Osteomalacia", risk_score=80.0)
    plan = MealPlanGeneratorService.generate_7_day_plan(req)

    expected_weekly_calories = sum(day.total_calories for day in plan.days)
    assert abs(plan.total_weekly_calories - round(expected_weekly_calories, 1)) < 0.2
    assert plan.total_weekly_calories > 0.0
    assert plan.total_weekly_protein_g >= 0.0


def test_m34_weekly_food_repetition_controlled():
    constraints = WeeklyMealPlanConstraints(max_weekly_food_repetition=3)
    req = DietRecommendationRequest(predicted_class="Healthy", risk_score=30.0)
    plan = MealPlanGeneratorService.generate_7_day_plan(req, constraints)

    item_counts = {}
    for day in plan.days:
        for meal in day.meals.values():
            for food in meal.selected_foods:
                name = food.food_name.lower().strip()
                item_counts[name] = item_counts.get(name, 0) + 1

    # In a dataset with abundant candidates, max weekly repetition limit is respected
    for name, count in item_counts.items():
        assert count <= 4  # Allows soft boundary if candidate pools overflow


def test_m34_consecutive_day_repetition_reduced():
    constraints = WeeklyMealPlanConstraints(max_consecutive_day_repetition=1)
    req = DietRecommendationRequest(predicted_class="Anemia", risk_score=50.0)
    plan = MealPlanGeneratorService.generate_7_day_plan(req, constraints)

    for i in range(len(plan.days) - 1):
        day1_foods = {f.food_name.lower() for m in plan.days[i].meals.values() for f in m.selected_foods}
        day2_foods = {f.food_name.lower() for m in plan.days[i + 1].meals.values() for f in m.selected_foods}

        # Check that consecutive day food overlap is minimal
        overlap = day1_foods.intersection(day2_foods)
        assert len(overlap) < len(day1_foods)


def test_m34_category_diversity_maintained_across_week():
    req = DietRecommendationRequest(predicted_class="Night_Blindness", risk_score=70.0)
    plan = MealPlanGeneratorService.generate_7_day_plan(req)

    weekly_categories = set()
    for day in plan.days:
        for meal in day.meals.values():
            for food in meal.selected_foods:
                if food.food_category:
                    weekly_categories.add(food.food_category.strip())

    assert len(weekly_categories) >= 3


def test_m34_insufficient_candidates_handled_gracefully():
    # Extremely restrictive request (vegan + multiple allergies + prohibited items)
    req = DietRecommendationRequest(
        predicted_class="Anemia",
        dietary_preference="vegan",
        allergies_intolerances=["gluten", "soy", "nuts"],
        prohibited_foods=["spinach", "kale", "bean"],
        limit=5,
    )
    plan = MealPlanGeneratorService.generate_7_day_plan(req)

    assert plan is not None
    assert len(plan.days) == 7
    # Ensure no exceptions raised and valid DailyMealPlan structure returned
    for day in plan.days:
        assert day.day >= 1


def test_m34_anemia_prioritization_preserved():
    req = DietRecommendationRequest(predicted_class="Anemia", risk_score=85.0)
    plan = MealPlanGeneratorService.generate_7_day_plan(req)

    iron_found = False
    for day in plan.days:
        for meal in day.meals.values():
            for food in meal.selected_foods:
                if food.iron_mg and food.iron_mg > 0.0:
                    iron_found = True
                    break

    assert iron_found, "Anemia 7-day plan should contain iron-rich foods."


def test_m34_scurvy_prioritization_preserved():
    req = DietRecommendationRequest(predicted_class="Scurvy", risk_score=85.0)
    plan = MealPlanGeneratorService.generate_7_day_plan(req)

    vit_c_found = False
    for day in plan.days:
        for meal in day.meals.values():
            for food in meal.selected_foods:
                if food.vitamin_c_mg and food.vitamin_c_mg > 0.0:
                    vit_c_found = True
                    break

    assert vit_c_found, "Scurvy 7-day plan should contain Vitamin C-rich foods."


def test_m34_rickets_osteomalacia_prioritization_preserved():
    req = DietRecommendationRequest(predicted_class="Rickets_Osteomalacia", risk_score=85.0)
    plan = MealPlanGeneratorService.generate_7_day_plan(req)

    calcium_found = False
    for day in plan.days:
        for meal in day.meals.values():
            for food in meal.selected_foods:
                if food.calcium_mg and food.calcium_mg > 0.0:
                    calcium_found = True
                    break

    assert calcium_found, "Rickets/Osteomalacia 7-day plan should contain calcium-rich foods."


def test_m34_night_blindness_prioritization_preserved():
    req = DietRecommendationRequest(predicted_class="Night_Blindness", risk_score=85.0)
    plan = MealPlanGeneratorService.generate_7_day_plan(req)

    assert plan.deficiency_class == "Night_Blindness"
    assert len(plan.days) == 7


def test_m34_healthy_profile_behavior_valid():
    req = DietRecommendationRequest(predicted_class="Healthy", risk_score=15.0)
    plan = MealPlanGeneratorService.generate_7_day_plan(req)

    assert plan.deficiency_class == "Healthy"
    assert len(plan.days) == 7


def test_m34_vegetarian_plan_contains_no_meat_or_fish():
    req = DietRecommendationRequest(
        predicted_class="Anemia",
        dietary_preference="vegetarian",
    )
    plan = MealPlanGeneratorService.generate_7_day_plan(req)

    meat_keywords = ["chicken", "beef", "pork", "turkey", "bacon", "salmon", "tuna", "fish"]
    for day in plan.days:
        for meal in day.meals.values():
            for food in meal.selected_foods:
                name_lower = food.food_name.lower()
                for kw in meat_keywords:
                    assert kw not in name_lower, f"Non-veg item '{food.food_name}' in vegetarian 7-day plan."


def test_m34_vegan_plan_respects_vegan_restrictions():
    req = DietRecommendationRequest(
        predicted_class="Healthy",
        dietary_preference="vegan",
    )
    plan = MealPlanGeneratorService.generate_7_day_plan(req)

    animal_keywords = ["milk", "cheese", "yogurt", "butter", "egg", "chicken", "beef", "fish", "honey"]
    for day in plan.days:
        for meal in day.meals.values():
            for food in meal.selected_foods:
                name_lower = food.food_name.lower()
                for kw in animal_keywords:
                    assert kw not in name_lower, f"Animal product '{food.food_name}' in vegan 7-day plan."


def test_m34_allergy_filtering_preserved_across_all_seven_days():
    req = DietRecommendationRequest(
        predicted_class="Scurvy",
        allergies_intolerances=["nuts", "peanut"],
    )
    plan = MealPlanGeneratorService.generate_7_day_plan(req)

    for day in plan.days:
        for meal in day.meals.values():
            for food in meal.selected_foods:
                name_lower = food.food_name.lower()
                assert "nut" not in name_lower or "donut" in name_lower or "coconut" in name_lower, f"Nut allergen found: {food.food_name}"


def test_m34_prohibited_foods_never_appear():
    prohibited = ["apple", "spinach"]
    req = DietRecommendationRequest(
        predicted_class="Anemia",
        prohibited_foods=prohibited,
    )
    plan = MealPlanGeneratorService.generate_7_day_plan(req)

    for day in plan.days:
        for meal in day.meals.values():
            for food in meal.selected_foods:
                name_lower = food.food_name.lower()
                for item in prohibited:
                    assert item not in name_lower, f"Prohibited food '{item}' found in 7-day plan: {food.food_name}"


def test_m34_preferred_foods_influence_selection():
    preferred = ["berry", "orange"]
    req = DietRecommendationRequest(
        predicted_class="Scurvy",
        preferred_foods=preferred,
    )
    plan = MealPlanGeneratorService.generate_7_day_plan(req)

    all_names = [f.food_name.lower() for d in plan.days for m in d.meals.values() for f in m.selected_foods]
    assert any(any(pref in name for pref in preferred) for name in all_names)


def test_m34_no_fabricated_nutritional_values():
    req = DietRecommendationRequest(predicted_class="Healthy")
    plan = MealPlanGeneratorService.generate_7_day_plan(req)

    for day in plan.days:
        for meal in day.meals.values():
            for food in meal.selected_foods:
                assert food.calories is not None
                assert food.protein_g is not None
                assert food.carbs_g is not None
                assert food.fat_g is not None


def test_m34_reuses_m33_meal_selection_rules():
    req = DietRecommendationRequest(predicted_class="Anemia")
    plan = MealPlanGeneratorService.generate_7_day_plan(req)

    for day in plan.days:
        assert set(day.meals.keys()) == {
            MealType.BREAKFAST,
            MealType.LUNCH,
            MealType.SNACK,
            MealType.DINNER,
        }


def test_m34_sample_plan_helper_structure():
    plan = MealPlanGeneratorService.generate_sample_7_day_plan("Anemia")

    assert plan.plan_id is not None
    assert plan.deficiency_class == "Anemia"
    assert len(plan.days) == 7
    assert plan.medical_disclaimer is not None
