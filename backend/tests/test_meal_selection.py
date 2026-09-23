import re
import pytest
from app.models.recommendation import DietRecommendationRequest

from app.models.meal import (
    MealType,
    MealSelectionConstraints,
    DailyMealPlan,
)
from app.services.meal_selection import MealSelectionService


def test_m33_all_four_meal_types_recognized():
    req = DietRecommendationRequest(predicted_class="Anemia", risk_score=75.0)
    plan: DailyMealPlan = MealSelectionService.select_daily_meals(req)

    assert set(plan.meals.keys()) == {
        MealType.BREAKFAST,
        MealType.LUNCH,
        MealType.SNACK,
        MealType.DINNER,
    }


def test_m33_breakfast_allocates_candidates():
    req = DietRecommendationRequest(predicted_class="Scurvy", risk_score=80.0)
    plan = MealSelectionService.select_daily_meals(req)

    breakfast_selection = plan.meals[MealType.BREAKFAST]
    assert breakfast_selection.meal_type == MealType.BREAKFAST
    assert len(breakfast_selection.selected_foods) > 0


def test_m33_lunch_allocates_candidates():
    req = DietRecommendationRequest(predicted_class="Rickets_Osteomalacia", risk_score=60.0)
    plan = MealSelectionService.select_daily_meals(req)

    lunch_selection = plan.meals[MealType.LUNCH]
    assert lunch_selection.meal_type == MealType.LUNCH
    assert len(lunch_selection.selected_foods) > 0


def test_m33_snack_allocates_candidates():
    req = DietRecommendationRequest(predicted_class="Night_Blindness", risk_score=70.0)
    plan = MealSelectionService.select_daily_meals(req)

    snack_selection = plan.meals[MealType.SNACK]
    assert snack_selection.meal_type == MealType.SNACK
    assert len(snack_selection.selected_foods) > 0


def test_m33_dinner_allocates_candidates():
    req = DietRecommendationRequest(predicted_class="Healthy", risk_score=20.0)
    plan = MealSelectionService.select_daily_meals(req)

    dinner_selection = plan.meals[MealType.DINNER]
    assert dinner_selection.meal_type == MealType.DINNER
    assert len(dinner_selection.selected_foods) > 0


def test_m33_meal_target_sizes_respected():
    constraints = MealSelectionConstraints(
        target_counts={
            MealType.BREAKFAST: 3,
            MealType.LUNCH: 2,
            MealType.SNACK: 1,
            MealType.DINNER: 3,
        }
    )
    req = DietRecommendationRequest(predicted_class="Anemia", risk_score=50.0)
    plan = MealSelectionService.select_daily_meals(req, constraints)

    assert len(plan.meals[MealType.BREAKFAST].selected_foods) == 3
    assert len(plan.meals[MealType.LUNCH].selected_foods) == 2
    assert len(plan.meals[MealType.SNACK].selected_foods) == 1
    assert len(plan.meals[MealType.DINNER].selected_foods) == 3


def test_m33_insufficient_candidates_handled_gracefully():
    # Strict combination that leaves very few candidate foods
    req = DietRecommendationRequest(
        predicted_class="Anemia",
        dietary_preference="vegan",
        allergies_intolerances=["gluten", "soy", "nuts", "seeds"],
        prohibited_foods=["spinach", "kale", "bean", "lentil"],
        limit=5,
    )
    # Should complete safely without raising an error even if targets cannot be fully filled with unique foods
    plan = MealSelectionService.select_daily_meals(req)
    assert plan is not None
    assert isinstance(plan.total_calories, float)


def test_m33_repetition_reduction_across_meals():
    req = DietRecommendationRequest(predicted_class="Anemia", risk_score=70.0)
    plan = MealSelectionService.select_daily_meals(req)

    all_selected_names = []
    for meal in plan.meals.values():
        for food in meal.selected_foods:
            all_selected_names.append(food.food_name.strip().lower())

    # Ensure that when abundant candidates exist, foods are not repeated unnecessarily in every meal
    unique_names = set(all_selected_names)
    assert len(unique_names) > 3


def test_m33_category_diversity_encouraged():
    constraints = MealSelectionConstraints(
        max_category_repetition_per_day=2,
        enforce_category_diversity=True,
    )
    req = DietRecommendationRequest(predicted_class="Healthy", risk_score=30.0)
    plan = MealSelectionService.select_daily_meals(req, constraints)

    categories = []
    for meal in plan.meals.values():
        for food in meal.selected_foods:
            if food.food_category:
                categories.append(food.food_category.strip())

    # Verify multiple distinct categories are present across meals
    unique_categories = set(categories)
    assert len(unique_categories) >= 2


def test_m33_deficiency_prioritization_maintained():
    req_anemia = DietRecommendationRequest(predicted_class="Anemia", risk_score=90.0)
    plan_anemia = MealSelectionService.select_daily_meals(req_anemia)

    # Check that iron-containing foods are present in anemia plan
    iron_values = [
        food.iron_mg
        for meal in plan_anemia.meals.values()
        for food in meal.selected_foods
        if food.iron_mg is not None
    ]
    assert any(val > 0.0 for val in iron_values)

    req_scurvy = DietRecommendationRequest(predicted_class="Scurvy", risk_score=90.0)
    plan_scurvy = MealSelectionService.select_daily_meals(req_scurvy)
    vit_c_values = [
        food.vitamin_c_mg
        for meal in plan_scurvy.meals.values()
        for food in meal.selected_foods
        if food.vitamin_c_mg is not None
    ]
    assert any(val > 0.0 for val in vit_c_values)


def test_m33_vegetarian_filtering_respected():
    req = DietRecommendationRequest(
        predicted_class="Healthy",
        dietary_preference="vegetarian",
    )
    plan = MealSelectionService.select_daily_meals(req)

    meat_keywords = ["chicken", "beef", "pork", "turkey", "bacon", "salmon", "tuna", "fish"]
    for meal in plan.meals.values():
        for food in meal.selected_foods:
            name_lower = food.food_name.lower()
            for kw in meat_keywords:
                assert kw not in name_lower, f"Vegetarian plan contained non-veg item: {food.food_name}"


def test_m33_vegan_filtering_respected():
    req = DietRecommendationRequest(
        predicted_class="Healthy",
        dietary_preference="vegan",
    )
    plan = MealSelectionService.select_daily_meals(req)

    animal_keywords = ["milk", "cheese", "yogurt", "butter", "egg", "chicken", "beef", "fish", "honey"]
    for meal in plan.meals.values():
        for food in meal.selected_foods:
            name_lower = food.food_name.lower()
            for kw in animal_keywords:
                assert kw not in name_lower, f"Vegan plan contained animal product: {food.food_name}"


def test_m33_allergy_filtering_respected():
    req = DietRecommendationRequest(
        predicted_class="Anemia",
        allergies_intolerances=["nuts", "peanut"],
    )
    plan = MealSelectionService.select_daily_meals(req)

    for meal in plan.meals.values():
        for food in meal.selected_foods:
            name_lower = food.food_name.lower()
            is_nut_item = bool(re.search(r"\b(nuts?|peanuts?|almonds?|walnuts?|cashews?|pecans?|hazelnuts?|pistachios?|macadamias?)\b", name_lower)) and not any(ex in name_lower for ex in ["coconut", "donut"])
            assert not is_nut_item, f"Nut allergen present in food: {food.food_name}"



def test_m33_prohibited_foods_filtering_respected():
    prohibited = ["apple", "spinach"]
    req = DietRecommendationRequest(
        predicted_class="Anemia",
        prohibited_foods=prohibited,
    )
    plan = MealSelectionService.select_daily_meals(req)

    for meal in plan.meals.values():
        for food in meal.selected_foods:
            name_lower = food.food_name.lower()
            for item in prohibited:
                assert item not in name_lower, f"Prohibited food '{item}' found in meal selection: {food.food_name}"


def test_m33_preferred_foods_influence_selection():
    preferred = ["berry", "orange"]
    req = DietRecommendationRequest(
        predicted_class="Scurvy",
        preferred_foods=preferred,
    )
    plan = MealSelectionService.select_daily_meals(req)

    all_names = [food.food_name.lower() for meal in plan.meals.values() for food in meal.selected_foods]
    # At least one preferred item should appear in daily selections
    assert any(any(pref in name for pref in preferred) for name in all_names)


def test_m33_nutritional_totals_aggregated_correctly():
    req = DietRecommendationRequest(predicted_class="Anemia")
    plan = MealSelectionService.select_daily_meals(req)

    expected_calories = sum(
        food.calories or 0.0 for meal in plan.meals.values() for food in meal.selected_foods
    )
    assert abs(plan.total_calories - round(expected_calories, 1)) < 0.2
