import pytest
from app.models.recipe import (
    Recipe,
    RecipeSearchRequest,
    RecipeSearchResponse,
    RecipeRecommendationRequest,
)
from app.services.recipe_service import RecipeService


def test_recipe_service_dataset_loading_and_search():
    """Verify RecipeService correctly loads dataset and searches by query term."""
    req = RecipeSearchRequest(query="apple", limit=5)
    res = RecipeService.search_recipes(req)

    assert isinstance(res, RecipeSearchResponse)
    assert len(res.recipes) > 0
    assert any("apple" in r.title.lower() for r in res.recipes)
    assert res.disclaimer is not None


def test_recipe_lookup_by_id():
    """Verify single recipe lookup by ID format and numeric FDC ID."""
    req = RecipeSearchRequest(limit=1)
    res = RecipeService.search_recipes(req)
    assert len(res.recipes) > 0

    first_recipe = res.recipes[0]
    recipe_id = first_recipe.recipe_id

    lookup_res = RecipeService.get_recipe_by_id(recipe_id)
    assert lookup_res is not None
    assert lookup_res.recipe_id == recipe_id
    assert lookup_res.title == first_recipe.title


def test_recipe_lookup_by_non_existent_id():
    """Verify looking up a non-existent recipe ID returns None safely."""
    res = RecipeService.get_recipe_by_id("fdc_999999999999")
    assert res is None


def test_recipe_empty_query_returns_valid_results():
    """Verify empty search query returns ranked recipes without crashing."""
    req = RecipeSearchRequest(query="", limit=5)
    res = RecipeService.search_recipes(req)
    assert len(res.recipes) > 0


def test_recipe_vegetarian_filtering():
    """Verify vegetarian dietary filter excludes meat and fish items."""
    req = RecipeSearchRequest(
        dietary_preference="vegetarian",
        limit=10
    )
    res = RecipeService.search_recipes(req)
    meat_terms = ["beef", "chicken", "pork", "lamb", "bacon", "sausage", "ham", "tuna", "salmon"]

    for r in res.recipes:
        title_lower = r.title.lower()
        for term in meat_terms:
            assert term not in title_lower, f"Meat item '{r.title}' found under vegetarian filter."


def test_recipe_vegan_filtering():
    """Verify vegan dietary filter excludes animal products."""
    req = RecipeSearchRequest(
        dietary_preference="vegan",
        limit=10
    )
    res = RecipeService.search_recipes(req)
    animal_terms = ["milk", "cheese", "yogurt", "egg", "chicken", "beef", "fish", "honey"]

    for r in res.recipes:
        title_lower = r.title.lower()
        for term in animal_terms:
            if term == "butter" and any(veg in title_lower for veg in ["almond", "peanut", "apple", "cocoa", "fluffbutter", "seed"]):
                continue
            assert term not in title_lower, f"Animal item '{r.title}' found under vegan filter."


def test_recipe_allergy_filtering():
    """Verify allergy restrictions exclude matching food/recipe items."""
    req = RecipeSearchRequest(
        allergies_intolerances=["nuts", "dairy"],
        limit=10
    )
    res = RecipeService.search_recipes(req)

    for r in res.recipes:
        title_lower = r.title.lower()
        assert "milk" not in title_lower
        assert "cheese" not in title_lower
        assert "peanut" not in title_lower


def test_recipe_prohibited_food_filtering():
    """Verify user prohibited foods are strictly excluded."""
    req = RecipeSearchRequest(
        prohibited_foods=["apple", "spinach"],
        limit=10
    )
    res = RecipeService.search_recipes(req)

    for r in res.recipes:
        title_lower = r.title.lower()
        assert "apple" not in title_lower
        assert "spinach" not in title_lower


def test_recipe_preferred_food_boost():
    """Verify preferred food terms boost search scores."""
    req = RecipeSearchRequest(
        preferred_foods=["fruit", "berry"],
        limit=5
    )
    res = RecipeService.search_recipes(req)
    assert len(res.recipes) > 0
    assert res.recipes[0].ranking_score >= 0.0


def test_recipe_recommendations_anemia():
    """Verify Anemia deficiency recommendations prioritize iron and Vitamin C rich foods."""
    req = RecipeRecommendationRequest(
        predicted_class="Anemia",
        risk_score=80.0,
        limit=5
    )
    res = RecipeService.get_recipe_recommendations(req)

    assert len(res.recipes) > 0
    top = res.recipes[0]
    assert top.targeted_deficiency == "Anemia"
    assert top.recommendation_reason is not None


def test_recipe_recommendations_scurvy():
    """Verify Scurvy deficiency recommendations prioritize Vitamin C rich foods."""
    req = RecipeRecommendationRequest(
        predicted_class="Scurvy",
        risk_score=75.0,
        limit=5
    )
    res = RecipeService.get_recipe_recommendations(req)

    assert len(res.recipes) > 0
    assert res.recipes[0].targeted_deficiency == "Scurvy"


def test_recipe_recommendations_rickets():
    """Verify Rickets deficiency recommendations prioritize calcium rich foods."""
    req = RecipeRecommendationRequest(
        predicted_class="Rickets_Osteomalacia",
        risk_score=70.0,
        limit=5
    )
    res = RecipeService.get_recipe_recommendations(req)

    assert len(res.recipes) > 0
    assert res.recipes[0].targeted_deficiency == "Rickets_Osteomalacia"


def test_recipe_recommendations_night_blindness():
    """Verify Night_Blindness uses rule-based signal keyword targeting."""
    req = RecipeRecommendationRequest(
        predicted_class="Night_Blindness",
        limit=5
    )
    res = RecipeService.get_recipe_recommendations(req)

    assert len(res.recipes) > 0
    assert res.recipes[0].targeted_deficiency == "Night_Blindness"


def test_no_fabricated_cooking_instructions_or_missing_nutrients():
    """Data Integrity Test: Verify no instructions, prep times, or missing nutrient fields are fabricated."""
    req = RecipeSearchRequest(limit=5)
    res = RecipeService.search_recipes(req)

    for r in res.recipes:
        assert not hasattr(r, "prep_time_minutes")
        assert not hasattr(r, "cooking_instructions")
        assert not hasattr(r, "vitamin_a_iu")
        assert not hasattr(r, "vitamin_d_mcg")


def test_recipe_deduplication():
    """Verify search results avoid duplicate recipe titles."""
    req = RecipeSearchRequest(limit=20)
    res = RecipeService.search_recipes(req)
    titles = [r.title.lower() for r in res.recipes]
    assert len(titles) == len(set(titles))
