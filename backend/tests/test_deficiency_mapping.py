"""
Unit Tests for Deficiency-to-Food Mapping Layer (Milestone 3 — Step M3.1)

Tests:
1. Deficiency-to-nutrient mappings for all 5 valid deficiency classes
2. Nutrient-to-food-source signals
3. Alternative food options generation
4. Verification of numeric vs rule-based signals (no fabricated Vitamin A / Vitamin D numeric fields)
5. Fallback for unknown deficiency classes
6. Integration with dietary preference and allergy filtering
"""

import pytest
from app.services.deficiency_mapping import (
    get_deficiency_mapping,
    get_all_target_nutrients,
    DEFICIENCY_MAPPING_REGISTRY,
    VALID_DEFICIENCY_CLASSES,
    DeficiencyNutrientMapping,
)
from app.services.recommendation_service import RecommendationService
from app.models.recommendation import DietRecommendationRequest


def test_valid_deficiency_classes_registered():
    """Verify all 5 ML deficiency classes are present in the mapping registry."""
    assert len(VALID_DEFICIENCY_CLASSES) == 5
    for def_class in VALID_DEFICIENCY_CLASSES:
        assert def_class in DEFICIENCY_MAPPING_REGISTRY
        mapping = get_deficiency_mapping(def_class)
        assert isinstance(mapping, DeficiencyNutrientMapping)
        assert mapping.deficiency_class == def_class


def test_anemia_nutrient_and_food_mapping():
    """Verify Anemia deficiency maps to iron_mg primary and vitamin_c_mg / protein_g supporting."""
    mapping = get_deficiency_mapping("Anemia")
    assert mapping.primary_nutrients == ["iron_mg"]
    assert "vitamin_c_mg" in mapping.supporting_nutrients
    assert "protein_g" in mapping.supporting_nutrients
    assert mapping.is_numeric_based is True
    assert "Legumes & Beans" in mapping.food_source_categories


def test_scurvy_nutrient_and_food_mapping():
    """Verify Scurvy deficiency maps to vitamin_c_mg primary and fiber_g supporting."""
    mapping = get_deficiency_mapping("Scurvy")
    assert mapping.primary_nutrients == ["vitamin_c_mg"]
    assert "fiber_g" in mapping.supporting_nutrients
    assert mapping.is_numeric_based is True
    assert "Citrus Fruits" in mapping.food_source_categories


def test_rickets_osteomalacia_nutrient_and_food_mapping():
    """Verify Rickets_Osteomalacia maps to calcium_mg primary and protein_g supporting without fabricated Vitamin D."""
    mapping = get_deficiency_mapping("Rickets_Osteomalacia")
    assert mapping.primary_nutrients == ["calcium_mg"]
    assert "protein_g" in mapping.supporting_nutrients
    assert mapping.is_numeric_based is True
    # Ensure no fabricated numeric vitamin d field is present in primary/supporting
    assert "vitamin_d_mcg" not in mapping.primary_nutrients
    assert "vitamin_d_ng_ml" not in mapping.primary_nutrients


def test_night_blindness_rule_based_signal_mapping():
    """Verify Night_Blindness is explicitly marked as rule-based signal matching due to dataset column limitations."""
    mapping = get_deficiency_mapping("Night_Blindness")
    assert mapping.is_numeric_based is False
    assert "vitamin_a_rule_signal" in mapping.primary_nutrients
    assert "carrot" in mapping.signal_keywords
    assert "spinach" in mapping.signal_keywords
    assert "kale" in mapping.signal_keywords
    assert "sweet potato" in mapping.signal_keywords
    assert "squash" in mapping.signal_keywords
    assert "pumpkin" in mapping.signal_keywords
    assert "liver" in mapping.signal_keywords


def test_healthy_baseline_mapping():
    """Verify Healthy deficiency class maps to health_score, fiber_g, and protein_g."""
    mapping = get_deficiency_mapping("Healthy")
    assert mapping.primary_nutrients == ["health_score"]
    assert "fiber_g" in mapping.supporting_nutrients
    assert "protein_g" in mapping.supporting_nutrients
    assert mapping.is_numeric_based is True


def test_unknown_deficiency_class_fallback():
    """Verify unknown or invalid deficiency strings safely fallback to Healthy mapping."""
    mapping_unknown = get_deficiency_mapping("Invalid_Deficiency_Name")
    assert mapping_unknown.deficiency_class == "Healthy"
    assert mapping_unknown.primary_nutrients == ["health_score"]

    mapping_none = get_deficiency_mapping(None)
    assert mapping_none.deficiency_class == "Healthy"


def test_alternative_food_options_generation():
    """Verify RecommendationService returns multiple alternative food recommendations for each deficiency."""
    for def_class in VALID_DEFICIENCY_CLASSES:
        req = DietRecommendationRequest(
            predicted_class=def_class,
            risk_score=75.0,
            risk_level="High Risk",
            limit=10
        )
        res = RecommendationService.get_recommendations(req)
        assert res.predicted_class == def_class
        assert len(res.recommended_foods) > 1, f"Expected multiple alternative foods for {def_class}"
        assert res.total_recommendations if hasattr(res, "total_recommendations") else len(res.recommended_foods) >= 1

        # Check deduplication & distinct names
        names = [f.food_name.lower() for f in res.recommended_foods]
        assert len(names) == len(set(names)), f"Found duplicate food names in {def_class} recommendations"


def test_dietary_filtering_integration():
    """Verify mapping layer works cleanly with vegetarian and vegan dietary preferences."""
    veg_req = DietRecommendationRequest(
        predicted_class="Anemia",
        risk_score=80.0,
        dietary_preference="vegetarian",
        limit=10
    )
    veg_res = RecommendationService.get_recommendations(veg_req)
    assert len(veg_res.recommended_foods) > 0
    for food in veg_res.recommended_foods:
        name_lower = food.food_name.lower()
        assert "beef" not in name_lower
        assert "chicken" not in name_lower
        assert "pork" not in name_lower

    vegan_req = DietRecommendationRequest(
        predicted_class="Rickets_Osteomalacia",
        risk_score=80.0,
        dietary_preference="vegan",
        limit=10
    )
    vegan_res = RecommendationService.get_recommendations(vegan_req)
    assert len(vegan_res.recommended_foods) > 0
    for food in vegan_res.recommended_foods:
        name_lower = food.food_name.lower()
        assert "milk" not in name_lower or "plant" in name_lower or "almond" in name_lower or "soy" in name_lower
        assert "cheese" not in name_lower


def test_allergy_filtering_integration():
    """Verify mapping layer works cleanly with allergy restrictions."""
    allergy_req = DietRecommendationRequest(
        predicted_class="Scurvy",
        risk_score=70.0,
        allergies_intolerances=["dairy", "nuts"],
        limit=10
    )
    allergy_res = RecommendationService.get_recommendations(allergy_req)
    assert len(allergy_res.recommended_foods) > 0
    for food in allergy_res.recommended_foods:
        name_lower = food.food_name.lower()
        assert "peanut" not in name_lower
        assert "almond" not in name_lower
        assert "milk" not in name_lower


def test_no_fabricated_nutrition_values():
    """Verify recommended food objects use authentic dataset fields without inventing Vitamin A or D numeric values."""
    req = DietRecommendationRequest(predicted_class="Night_Blindness", risk_score=50.0, limit=5)
    res = RecommendationService.get_recommendations(req)
    for food in res.recommended_foods:
        # Check that standard numeric fields are authentic numbers or None
        assert isinstance(food.iron_mg, (float, int))
        assert isinstance(food.vitamin_c_mg, (float, int))
        assert isinstance(food.calcium_mg, (float, int))
        assert isinstance(food.ranking_score, float)
        # Ensure no fabricated vitamin_a_iu or vitamin_d_iu attribute was added
        assert not hasattr(food, "vitamin_a_iu")
        assert not hasattr(food, "vitamin_d_iu")
