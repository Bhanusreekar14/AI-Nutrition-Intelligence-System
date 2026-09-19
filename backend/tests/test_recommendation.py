import pytest
from app.models.recommendation import DietRecommendationRequest, DietRecommendationResponse
from app.services.recommendation_service import RecommendationService

def test_anemia_recommendations_contain_valid_food_records():
    req = DietRecommendationRequest(
        predicted_class="Anemia",
        risk_level="High Risk",
        risk_score=75.0,
        dietary_preference="omnivore",
        limit=5
    )
    res = RecommendationService.get_recommendations(req)
    assert isinstance(res, DietRecommendationResponse)
    assert res.predicted_class == "Anemia"
    assert "iron_mg" in res.targeted_nutrients
    assert len(res.recommended_foods) > 0
    assert len(res.recommended_foods) <= 5
    for food in res.recommended_foods:
        assert food.food_name
        assert "iron" in food.recommendation_reason.lower()

def test_scurvy_recommendations_prioritize_vitamin_c():
    req = DietRecommendationRequest(
        predicted_class="Scurvy",
        risk_level="High Risk",
        risk_score=80.0,
        limit=5
    )
    res = RecommendationService.get_recommendations(req)
    assert res.predicted_class == "Scurvy"
    assert "vitamin_c_mg" in res.targeted_nutrients
    assert len(res.recommended_foods) > 0
    for food in res.recommended_foods:
        assert food.vitamin_c_mg >= 0.0
        assert "vitamin c" in food.recommendation_reason.lower()

def test_rickets_osteomalacia_recommendations_use_calcium():
    req = DietRecommendationRequest(
        predicted_class="Rickets_Osteomalacia",
        risk_level="Moderate Risk",
        risk_score=55.0,
        limit=5
    )
    res = RecommendationService.get_recommendations(req)
    assert res.predicted_class == "Rickets_Osteomalacia"
    assert "calcium_mg" in res.targeted_nutrients
    assert len(res.recommended_foods) > 0
    for food in res.recommended_foods:
        assert food.calcium_mg >= 0.0
        assert "calcium" in food.recommendation_reason.lower()

def test_night_blindness_uses_rule_signal_without_inventing_vitamin_a():
    req = DietRecommendationRequest(
        predicted_class="Night_Blindness",
        risk_level="High Risk",
        risk_score=70.0,
        limit=5
    )
    res = RecommendationService.get_recommendations(req)
    assert res.predicted_class == "Night_Blindness"
    assert "vitamin_a_rule_signal" in res.targeted_nutrients
    assert len(res.recommended_foods) > 0
    for food in res.recommended_foods:
        # Check that recommendation reason explicitly notes category/ingredient signal
        assert "signal" in food.recommendation_reason.lower() or "vitamin-a" in food.recommendation_reason.lower()
        # Verify model does not contain fake vitamin_a_mcg attribute
        assert not hasattr(food, "vitamin_a_mcg")

def test_healthy_recommendations_work():
    req = DietRecommendationRequest(
        predicted_class="Healthy",
        risk_level="Low Risk",
        risk_score=15.0,
        limit=5
    )
    res = RecommendationService.get_recommendations(req)
    assert res.predicted_class == "Healthy"
    assert "health_score" in res.targeted_nutrients
    assert len(res.recommended_foods) > 0

def test_vegetarian_filtering_excludes_meat_fish():
    req = DietRecommendationRequest(
        predicted_class="Anemia",
        dietary_preference="vegetarian",
        limit=10
    )
    res = RecommendationService.get_recommendations(req)
    non_veg_terms = ["beef", "pork", "chicken", "turkey", "lamb", "bacon", "sausage", "tuna", "salmon", "shrimp"]
    for food in res.recommended_foods:
        name_lower = food.food_name.lower()
        for term in non_veg_terms:
            assert term not in name_lower, f"Non-vegetarian item '{food.food_name}' found for vegetarian preference."

def test_vegan_filtering_excludes_animal_products():
    req = DietRecommendationRequest(
        predicted_class="Scurvy",
        dietary_preference="vegan",
        limit=10
    )
    res = RecommendationService.get_recommendations(req)
    animal_terms = ["milk", "cheese", "butter", "yogurt", "cream", "egg", "beef", "chicken", "fish"]
    for food in res.recommended_foods:
        name_lower = food.food_name.lower()
        for term in animal_terms:
            assert term not in name_lower, f"Animal-derived item '{food.food_name}' found for vegan preference."

def test_allergy_filtering_removes_matching_foods():
    req = DietRecommendationRequest(
        predicted_class="Rickets_Osteomalacia",
        allergies_intolerances=["dairy", "nuts"],
        limit=10
    )
    res = RecommendationService.get_recommendations(req)
    dairy_nut_terms = ["milk", "cheese", "butter", "cream", "yogurt", "peanut", "almond", "cashew", "walnut"]
    for food in res.recommended_foods:
        name_lower = food.food_name.lower()
        for term in dairy_nut_terms:
            assert term not in name_lower, f"Allergenic item '{food.food_name}' found when dairy/nuts filtered."

def test_result_count_is_limited():
    req = DietRecommendationRequest(
        predicted_class="Anemia",
        limit=3
    )
    res = RecommendationService.get_recommendations(req)
    assert len(res.recommended_foods) <= 3

def test_duplicate_food_names_avoided():
    req = DietRecommendationRequest(
        predicted_class="Anemia",
        limit=15
    )
    res = RecommendationService.get_recommendations(req)
    names = [f.food_name.lower() for f in res.recommended_foods]
    assert len(names) == len(set(names))

def test_invalid_deficiency_class_handled_safely():
    req = DietRecommendationRequest(
        predicted_class="UnknownDeficiency123",
        limit=5
    )
    res = RecommendationService.get_recommendations(req)
    assert res.predicted_class == "Healthy"
    assert len(res.recommended_foods) > 0

def test_recommendation_output_is_deterministic():
    req = DietRecommendationRequest(
        predicted_class="Anemia",
        risk_level="High Risk",
        risk_score=75.0,
        dietary_preference="vegetarian",
        allergies_intolerances=["nuts"],
        limit=5
    )
    res1 = RecommendationService.get_recommendations(req)
    res2 = RecommendationService.get_recommendations(req)

    assert [f.food_name for f in res1.recommended_foods] == [f.food_name for f in res2.recommended_foods]
    assert [f.ranking_score for f in res1.recommended_foods] == [f.ranking_score for f in res2.recommended_foods]

def test_medical_disclaimer_present():
    req = DietRecommendationRequest(
        predicted_class="Anemia",
        limit=1
    )
    res = RecommendationService.get_recommendations(req)
    assert "educational purposes" in res.medical_disclaimer.lower()
    assert "medical diagnoses" in res.medical_disclaimer.lower()

def test_m32_prohibited_food_filtering():
    """Verify prohibited food exclusions remove matching food items before ranking."""
    req = DietRecommendationRequest(
        predicted_class="Anemia",
        prohibited_foods=["spinach", "beef"],
        limit=10
    )
    res = RecommendationService.get_recommendations(req)
    assert len(res.recommended_foods) > 0
    for food in res.recommended_foods:
        name_lower = food.food_name.lower()
        assert "spinach" not in name_lower
        assert "beef" not in name_lower

def test_m32_user_food_preferences_boosting():
    """Verify preferred food keywords boost matching item ranking scores."""
    req_pref = DietRecommendationRequest(
        predicted_class="Anemia",
        preferred_foods=["bean"],
        limit=10
    )
    res_pref = RecommendationService.get_recommendations(req_pref)
    assert len(res_pref.recommended_foods) > 0
    pref_items = [f for f in res_pref.recommended_foods if "bean" in f.food_name.lower()]
    assert len(pref_items) > 0

def test_m32_risk_aware_prioritization_scaling():
    """Verify higher risk scores increase ranking score for nutrient-rich items."""
    req_low = DietRecommendationRequest(
        predicted_class="Anemia",
        risk_score=10.0,
        risk_level="Low Risk",
        limit=5
    )
    res_low = RecommendationService.get_recommendations(req_low)

    req_high = DietRecommendationRequest(
        predicted_class="Anemia",
        risk_score=90.0,
        risk_level="Very High Risk",
        limit=5
    )
    res_high = RecommendationService.get_recommendations(req_high)

    assert len(res_low.recommended_foods) > 0
    assert len(res_high.recommended_foods) > 0
    # Top food in high risk should have equal or higher ranking score due to risk multiplier
    assert res_high.recommended_foods[0].ranking_score >= res_low.recommended_foods[0].ranking_score
