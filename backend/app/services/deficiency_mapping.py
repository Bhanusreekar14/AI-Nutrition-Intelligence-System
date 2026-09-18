"""
Deficiency-to-Food Mapping Layer for AI-Nutrition-Intelligence-System.
Milestone 3 — Step M3.1

Architecture:
Deficiency Class
    ↓
Relevant Nutrients (Primary & Supporting)
    ↓
Food-Source Signals (Numeric Ranking Metrics or Keyword Rule Signals)
    ↓
Suitable Foods & Alternative Food Options
"""

from typing import Dict, List, Set, Any
from dataclasses import dataclass, field

# 1. Valid Deficiency Classes evaluated by XGBoost ML Model
VALID_DEFICIENCY_CLASSES = {
    "Anemia",
    "Healthy",
    "Night_Blindness",
    "Rickets_Osteomalacia",
    "Scurvy"
}

@dataclass
class DeficiencyNutrientMapping:
    deficiency_class: str
    primary_nutrients: List[str]
    supporting_nutrients: List[str]
    is_numeric_based: bool
    signal_keywords: List[str] = field(default_factory=list)
    food_source_categories: List[str] = field(default_factory=list)
    dietary_advice: List[str] = field(default_factory=list)
    ranking_weights: Dict[str, float] = field(default_factory=dict)

# 2. Strict Deficiency-to-Nutrient Mappings
# Uses ONLY numeric fields present in datasets/food_nutrition/food_nutrition.csv:
# ['calories', 'carbs_g', 'calcium_mg', 'fat_g', 'protein_g', 'saturated_fat_g',
#  'vitamin_c_mg', 'fiber_g', 'iron_mg', 'sodium_mg', 'sugar_g', 'cholesterol_mg', 'health_score']
#
# Dataset does NOT provide numeric Vitamin A, Vitamin D, Vitamin B12, or Folate.
# Rule-based category/ingredient signals are used where numeric fields are absent.
DEFICIENCY_MAPPING_REGISTRY: Dict[str, DeficiencyNutrientMapping] = {
    "Anemia": DeficiencyNutrientMapping(
        deficiency_class="Anemia",
        primary_nutrients=["iron_mg"],
        supporting_nutrients=["vitamin_c_mg", "protein_g"],
        is_numeric_based=True,
        signal_keywords=["spinach", "legumes", "beans", "lentils", "fortified", "beef", "liver"],
        food_source_categories=["Legumes & Beans", "Dark Leafy Greens", "Meats & Poultry", "Fortified Grains"],
        dietary_advice=[
            "Include non-heme iron sources (spinach, legumes, fortified grains) paired with Vitamin C to enhance absorption.",
            "Avoid consuming coffee or tea at the exact same time as iron-rich meals, as tannins can inhibit iron uptake."
        ],
        ranking_weights={"iron_mg": 5.0, "vitamin_c_mg": 0.5, "protein_g": 1.5, "health_score": 0.4}
    ),
    "Scurvy": DeficiencyNutrientMapping(
        deficiency_class="Scurvy",
        primary_nutrients=["vitamin_c_mg"],
        supporting_nutrients=["fiber_g"],
        is_numeric_based=True,
        signal_keywords=["citrus", "orange", "lemon", "bell pepper", "strawberry", "broccoli", "kiwi"],
        food_source_categories=["Citrus Fruits", "Berries", "Cruciferous Vegetables", "Peppers"],
        dietary_advice=[
            "Incorporate fresh citrus fruits, bell peppers, strawberries, and broccoli into daily meals to boost natural Vitamin C intake.",
            "Raw or lightly steamed vegetables retain significantly higher Vitamin C levels compared to prolonged boiling."
        ],
        ranking_weights={"vitamin_c_mg": 2.5, "fiber_g": 2.0, "health_score": 0.4}
    ),
    "Rickets_Osteomalacia": DeficiencyNutrientMapping(
        deficiency_class="Rickets_Osteomalacia",
        primary_nutrients=["calcium_mg"],
        supporting_nutrients=["protein_g"],
        is_numeric_based=True,
        signal_keywords=["dairy", "milk", "cheese", "yogurt", "tofu", "fortified plant milk", "collard greens"],
        food_source_categories=["Dairy Products", "Fortified Plant Milks", "Tofu & Soy", "Dark Leafy Greens"],
        dietary_advice=[
            "Choose calcium-dense foods such as dairy products, fortified plant milks, tofu, and dark leafy greens.",
            "Ensure adequate safe sun exposure or dietary sources to support bone health and calcium uptake."
        ],
        ranking_weights={"calcium_mg": 0.3, "protein_g": 1.5, "health_score": 0.4}
    ),
    "Night_Blindness": DeficiencyNutrientMapping(
        deficiency_class="Night_Blindness",
        primary_nutrients=["vitamin_a_rule_signal"],
        supporting_nutrients=["fiber_g", "protein_g"],
        is_numeric_based=False,  # Rule-based ingredient/category signal because food dataset lacks numeric Vitamin A
        signal_keywords=[
            "carrot", "spinach", "kale", "sweet potato", "squash", "pumpkin",
            "liver", "cantaloupe", "mango", "papaya", "apricot", "collard", "turnip green"
        ],
        food_source_categories=["Orange Vegetables", "Dark Leafy Greens", "Organ Meats", "Orange Fruits"],
        dietary_advice=[
            "Focus on orange and dark leafy green vegetables (such as carrots, sweet potatoes, spinach, and squash) rich in provitamin A carotenoids.",
            "Consuming carotenoid-rich vegetables with a small amount of healthy fats (like olive oil) enhances Vitamin A bioavailability."
        ],
        ranking_weights={"health_score": 0.6, "fiber_g": 2.0, "protein_g": 1.5}
    ),
    "Healthy": DeficiencyNutrientMapping(
        deficiency_class="Healthy",
        primary_nutrients=["health_score"],
        supporting_nutrients=["fiber_g", "protein_g"],
        is_numeric_based=True,
        signal_keywords=["whole grain", "vegetables", "lean protein", "fruits", "nuts", "seeds"],
        food_source_categories=["Whole Grains", "Fresh Vegetables", "Lean Proteins", "Nuts & Seeds"],
        dietary_advice=[
            "Maintain a balanced diet rich in dietary fiber, high-quality proteins, and diverse whole foods.",
            "Limit excessive sodium, added sugars, and saturated fats to support long-term metabolic and cardiovascular health."
        ],
        ranking_weights={"health_score": 0.6, "fiber_g": 3.0, "protein_g": 2.0, "sodium_mg": -0.01, "saturated_fat_g": -0.5}
    )
}


def get_deficiency_mapping(deficiency_class: str) -> DeficiencyNutrientMapping:
    """
    Retrieves the structured deficiency-to-nutrient and signal mapping.
    Fallback to 'Healthy' for unknown or unclassified input values.
    """
    if not deficiency_class or deficiency_class not in DEFICIENCY_MAPPING_REGISTRY:
        return DEFICIENCY_MAPPING_REGISTRY["Healthy"]
    return DEFICIENCY_MAPPING_REGISTRY[deficiency_class]


def get_all_target_nutrients(deficiency_class: str) -> List[str]:
    """
    Returns combined list of primary and supporting nutrients/signals for a deficiency.
    """
    mapping = get_deficiency_mapping(deficiency_class)
    return mapping.primary_nutrients + mapping.supporting_nutrients
