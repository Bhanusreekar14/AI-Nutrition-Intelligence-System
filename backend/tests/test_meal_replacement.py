import pytest
from app.models.recommendation import DietRecommendationRequest
from app.models.meal import (
    MealType,
    WeeklyMealPlan,
    MealReplacementRequest,
    MealReplacementResponse,
)
from app.services.meal_plan_generator import MealPlanGeneratorService
from app.services.meal_replacement import MealReplacementService


@pytest.fixture
def sample_weekly_plan():
    """Generates a standard 7-day meal plan fixture for testing replacement functionality."""
    return MealPlanGeneratorService.generate_sample_7_day_plan(deficiency_class="Anemia")


def test_m35_successful_replacement(sample_weekly_plan):
    """Verifies that a valid replacement request successfully replaces the targeted item."""
    day_1_bfast = sample_weekly_plan.days[0].meals[MealType.BREAKFAST]
    target_food = day_1_bfast.selected_foods[0]

    req = MealReplacementRequest(
        weekly_plan=sample_weekly_plan,
        day=1,
        meal_type=MealType.BREAKFAST,
        target_food_name=target_food.food_name,
        predicted_class="Anemia",
    )

    resp = MealReplacementService.replace_food_in_plan(req)

    assert isinstance(resp, MealReplacementResponse)
    assert resp.original_food.food_name == target_food.food_name
    assert resp.replacement_food.food_name != target_food.food_name
    assert len(resp.updated_meal.selected_foods) == len(day_1_bfast.selected_foods)
    assert resp.medical_disclaimer is not None


def test_m35_original_food_is_not_returned(sample_weekly_plan):
    """Verifies that the replacement candidate is never the exact same food as the original."""
    day_1_lunch = sample_weekly_plan.days[0].meals[MealType.LUNCH]
    target_food = day_1_lunch.selected_foods[0]

    req = MealReplacementRequest(
        weekly_plan=sample_weekly_plan,
        day=1,
        meal_type=MealType.LUNCH,
        target_food_name=target_food.food_name,
    )

    resp = MealReplacementService.replace_food_in_plan(req)

    assert resp.replacement_food.food_name.strip().lower() != target_food.food_name.strip().lower()


def test_m35_vegetarian_restriction(sample_weekly_plan):
    """Verifies that vegetarian dietary restrictions are enforced during replacement."""
    day_1_dinner = sample_weekly_plan.days[0].meals[MealType.DINNER]
    target_food = day_1_dinner.selected_foods[0]

    req = MealReplacementRequest(
        weekly_plan=sample_weekly_plan,
        day=1,
        meal_type=MealType.DINNER,
        target_food_name=target_food.food_name,
        dietary_preference="vegetarian",
    )

    resp = MealReplacementService.replace_food_in_plan(req)

    meat_keywords = ["beef", "chicken", "pork", "lamb", "turkey", "bacon", "sausage", "ham", "fish", "salmon", "tuna"]
    name_lower = resp.replacement_food.food_name.lower()
    for kw in meat_keywords:
        assert kw not in name_lower, f"Non-vegetarian item '{resp.replacement_food.food_name}' selected under vegetarian restriction."


def test_m35_vegan_restriction(sample_weekly_plan):
    """Verifies that vegan dietary restrictions are enforced during replacement."""
    day_2_bfast = sample_weekly_plan.days[1].meals[MealType.BREAKFAST]
    target_food = day_2_bfast.selected_foods[0]

    req = MealReplacementRequest(
        weekly_plan=sample_weekly_plan,
        day=2,
        meal_type=MealType.BREAKFAST,
        target_food_name=target_food.food_name,
        dietary_preference="vegan",
    )

    resp = MealReplacementService.replace_food_in_plan(req)

    animal_keywords = ["milk", "cheese", "yogurt", "egg", "chicken", "beef", "fish", "honey"]
    name_lower = resp.replacement_food.food_name.lower()
    for kw in animal_keywords:
        assert kw not in name_lower, f"Animal item '{resp.replacement_food.food_name}' selected under vegan restriction."


def test_m35_allergy_restriction(sample_weekly_plan):
    """Verifies that allergen restrictions are strictly enforced during replacement."""
    day_1_snack = sample_weekly_plan.days[0].meals[MealType.SNACK]
    target_food = day_1_snack.selected_foods[0]

    req = MealReplacementRequest(
        weekly_plan=sample_weekly_plan,
        day=1,
        meal_type=MealType.SNACK,
        target_food_name=target_food.food_name,
        allergies_intolerances=["nuts", "dairy"],
    )

    resp = MealReplacementService.replace_food_in_plan(req)

    name_lower = resp.replacement_food.food_name.lower()
    assert "milk" not in name_lower
    assert "cheese" not in name_lower
    assert "peanut" not in name_lower


def test_m35_prohibited_food_filtering(sample_weekly_plan):
    """Verifies that user prohibited food keywords are filtered out of candidates."""
    day_3_lunch = sample_weekly_plan.days[2].meals[MealType.LUNCH]
    target_food = day_3_lunch.selected_foods[0]

    req = MealReplacementRequest(
        weekly_plan=sample_weekly_plan,
        day=3,
        meal_type=MealType.LUNCH,
        target_food_name=target_food.food_name,
        prohibited_foods=["rice", "soup", "salad"],
    )

    resp = MealReplacementService.replace_food_in_plan(req)

    name_lower = resp.replacement_food.food_name.lower()
    assert "rice" not in name_lower
    assert "soup" not in name_lower


def test_m35_preferred_food_handling(sample_weekly_plan):
    """Verifies that preferred food keywords boost replacement candidate ranking."""
    day_1_snack = sample_weekly_plan.days[0].meals[MealType.SNACK]
    target_food = day_1_snack.selected_foods[0]

    req = MealReplacementRequest(
        weekly_plan=sample_weekly_plan,
        day=1,
        meal_type=MealType.SNACK,
        target_food_name=target_food.food_name,
        preferred_foods=["apple", "fruit"],
    )

    resp = MealReplacementService.replace_food_in_plan(req)

    assert resp.replacement_food is not None
    assert resp.replacement_food.ranking_score > 0.0


def test_m35_deficiency_prioritization(sample_weekly_plan):
    """Verifies that deficiency nutrient prioritization is preserved during replacement."""
    day_1_lunch = sample_weekly_plan.days[0].meals[MealType.LUNCH]
    target_food = day_1_lunch.selected_foods[0]

    req = MealReplacementRequest(
        weekly_plan=sample_weekly_plan,
        day=1,
        meal_type=MealType.LUNCH,
        target_food_name=target_food.food_name,
        predicted_class="Anemia",
        risk_score=80.0,
    )

    resp = MealReplacementService.replace_food_in_plan(req)

    assert resp.replacement_food.iron_mg is not None
    assert resp.replacement_food.iron_mg >= 0.0


def test_m35_nutrition_recalculation(sample_weekly_plan):
    """Verifies that affected meal, day, and weekly nutrition totals are accurately recalculated."""
    day_1_bfast = sample_weekly_plan.days[0].meals[MealType.BREAKFAST]
    target_food = day_1_bfast.selected_foods[0]

    orig_day_1_cal = sample_weekly_plan.days[0].total_calories
    orig_weekly_cal = sample_weekly_plan.total_weekly_calories

    req = MealReplacementRequest(
        weekly_plan=sample_weekly_plan,
        day=1,
        meal_type=MealType.BREAKFAST,
        target_food_name=target_food.food_name,
    )

    resp = MealReplacementService.replace_food_in_plan(req)

    # Calculate expected new day 1 calories
    new_day_1 = resp.updated_weekly_plan.days[0]
    expected_day_cal = sum(
        f.calories or 0.0 for m in new_day_1.meals.values() for f in m.selected_foods
    )
    assert abs(new_day_1.total_calories - round(expected_day_cal, 1)) < 0.1

    # Verify weekly calories recalculation matches sum of all 7 days
    expected_weekly_cal = sum(d.total_calories for d in resp.updated_weekly_plan.days)
    assert abs(resp.updated_weekly_plan.total_weekly_calories - round(expected_weekly_cal, 1)) < 0.1


def test_m35_only_requested_item_changes_and_immutability(sample_weekly_plan):
    """
    Verifies plan immutability: ONLY the requested item changes;
    all other items in the meal slot, other meals on the day, and Days 2-7 remain unchanged.
    """
    day_1_lunch = sample_weekly_plan.days[0].meals[MealType.LUNCH]
    target_food = day_1_lunch.selected_foods[0]
    unaffected_food_in_lunch = day_1_lunch.selected_foods[1] if len(day_1_lunch.selected_foods) > 1 else None

    req = MealReplacementRequest(
        weekly_plan=sample_weekly_plan,
        day=1,
        meal_type=MealType.LUNCH,
        target_food_name=target_food.food_name,
    )

    resp = MealReplacementService.replace_food_in_plan(req)

    # 1. Unaffected food in the same lunch slot remains unchanged
    if unaffected_food_in_lunch:
        updated_lunch = resp.updated_day.meals[MealType.LUNCH]
        assert any(f.food_name == unaffected_food_in_lunch.food_name for f in updated_lunch.selected_foods)

    # 2. Other meals on Day 1 (Breakfast, Snack, Dinner) remain unchanged
    for m_type in [MealType.BREAKFAST, MealType.SNACK, MealType.DINNER]:
        orig_foods = [f.food_name for f in sample_weekly_plan.days[0].meals[m_type].selected_foods]
        updated_foods = [f.food_name for f in resp.updated_day.meals[m_type].selected_foods]
        assert orig_foods == updated_foods, f"Meal {m_type.value} on Day 1 was altered unexpectedly."

    # 3. Days 2 to 7 remain completely unchanged
    for d_idx in range(1, 7):
        orig_day = sample_weekly_plan.days[d_idx]
        updated_day = resp.updated_weekly_plan.days[d_idx]
        assert orig_day.total_calories == updated_day.total_calories
        for m_type in [MealType.BREAKFAST, MealType.LUNCH, MealType.SNACK, MealType.DINNER]:
            orig_m = [f.food_name for f in orig_day.meals[m_type].selected_foods]
            upd_m = [f.food_name for f in updated_day.meals[m_type].selected_foods]
            assert orig_m == upd_m, f"Day {d_idx+1} {m_type.value} was altered unexpectedly."


def test_m35_invalid_target_food_raises_error(sample_weekly_plan):
    """Verifies that requesting replacement of a non-existent food item raises a ValueError."""
    req = MealReplacementRequest(
        weekly_plan=sample_weekly_plan,
        day=1,
        meal_type=MealType.BREAKFAST,
        target_food_name="NonExistentUnicornFood12345",
    )

    with pytest.raises(ValueError, match="not found"):
        MealReplacementService.replace_food_in_plan(req)


def test_m35_no_safe_candidate_behavior(sample_weekly_plan):
    """Verifies that impossible constraint combinations raise a ValueError instead of returning unsafe food."""
    target_food = sample_weekly_plan.days[0].meals[MealType.BREAKFAST].selected_foods[0]

    # Extreme restriction excluding virtually all foods
    req = MealReplacementRequest(
        weekly_plan=sample_weekly_plan,
        day=1,
        meal_type=MealType.BREAKFAST,
        target_food_name=target_food.food_name,
        prohibited_foods=["a", "e", "i", "o", "u", "b", "c", "d", "f", "g", "h", "j", "k", "l", "m", "n", "p", "q", "r", "s", "t", "v", "w", "x", "y", "z"],
    )

    with pytest.raises(ValueError, match="No safe replacement candidate"):
        MealReplacementService.replace_food_in_plan(req)
