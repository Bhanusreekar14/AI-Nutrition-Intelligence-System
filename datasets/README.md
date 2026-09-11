# AI Nutrition Intelligence System - Datasets Directory

This directory contains the organized datasets for the **AI Nutrition Intelligence System**. The datasets are structured cleanly into logical subdirectories according to their specific application role (ML Training, Food Nutrition Lookup, Allergen Checking, Optional/Future Features, and Archives).

---

## 📁 Directory Structure

```
datasets/
├── deficiency/
│   └── deficiency_preprocessed.csv
├── food_nutrition/
│   └── food_nutrition.csv
├── allergens/
│   └── food_allergens.csv
├── optional/
│   ├── food_nutriscore.csv
│   ├── food_health_scores_allergens.csv
│   └── healthy_foods_database.csv
├── archive/
│   └── vitamin_deficiency_preprocessed_integer.csv
└── README.md
```

---

## 📊 Dataset Catalog & Usage Summary

| Dataset File Path | Rows × Columns | File Size | Primary Purpose & Usage | Category |
| :--- | :---: | :---: | :--- | :--- |
| [`deficiency/deficiency_preprocessed.csv`](file:///Users/kommusaishruthin/Desktop/Infosys/datasets/deficiency/deficiency_preprocessed.csv) | 4,000 × 49 | ~571 KB | **Machine Learning Model Training** dataset for predicting nutritional deficiency risks based on demographics, RDA percentages, serum levels, and reported symptoms. | ML Deficiency Training Data |
| [`food_nutrition/food_nutrition.csv`](file:///Users/kommusaishruthin/Desktop/Infosys/datasets/food_nutrition/food_nutrition.csv) | 40,000 × 24 | ~16.27 MB | **Food Nutrition Lookup** database containing comprehensive USDA food composition details, calories, macronutrients, and micronutrients. | Food Nutrition Lookup Data |
| [`allergens/food_allergens.csv`](file:///Users/kommusaishruthin/Desktop/Infosys/datasets/allergens/food_allergens.csv) | 3,332 × 9 | ~301 KB | **Allergen Checking** lookup dataset containing product names, brands, allergen descriptions, and boolean allergen flags (gluten, dairy, nuts, soy, eggs, fish). | Allergen Data |
| [`optional/food_nutriscore.csv`](file:///Users/kommusaishruthin/Desktop/Infosys/datasets/optional/food_nutriscore.csv) | 4,997 × 11 | ~691 KB | **NutriScore & Dietary Restrictions** dataset containing product categories, NutriScore grades (A-E), NOVA group classifications, and allergen flags for future rating features. | Optional / Future Dataset |
| [`optional/food_health_scores_allergens.csv`](file:///Users/kommusaishruthin/Desktop/Infosys/datasets/optional/food_health_scores_allergens.csv) | 4,997 × 24 | ~2.09 MB | **Extended Health Scores & NutriScore** dataset with 100g nutritional breakdowns, EcoScore, NutriScore, and allergen flags. | Optional / Future Dataset |
| [`optional/healthy_foods_database.csv`](file:///Users/kommusaishruthin/Desktop/Infosys/datasets/optional/healthy_foods_database.csv) | 9,028 × 10 | ~845 KB | **Healthy Foods Lookup** dataset with food categories, macronutrients, sodium levels, and health scores. | Optional / Future Dataset |
| [`archive/vitamin_deficiency_preprocessed_integer.csv`](file:///Users/kommusaishruthin/Desktop/Infosys/datasets/archive/vitamin_deficiency_preprocessed_integer.csv) | 4,000 × 49 | ~459 KB | **Integer-Rounded Deficiency Dataset** variant containing integer-truncated RDA and biomarker values. Preserved in archive to prevent data loss. | Archived Dataset |

---

## 🔍 Dataset Comparison & Duplicate Analysis

1. **Nutritional Deficiency Datasets (4,000 × 49)**:
   - **File 1**: [`datasets/deficiency/deficiency_preprocessed.csv`](file:///Users/kommusaishruthin/Desktop/Infosys/datasets/deficiency/deficiency_preprocessed.csv) (Unrounded float precision for BMI, RDA %, serum biomarker levels). Selected as the **Main Deficiency ML Dataset**.
   - **File 2**: [`datasets/archive/vitamin_deficiency_preprocessed_integer.csv`](file:///Users/kommusaishruthin/Desktop/Infosys/datasets/archive/vitamin_deficiency_preprocessed_integer.csv) (Integer-rounded variant). Moved to `datasets/archive/` to preserve data history without polluting active training datasets.
   - *Result*: 46,129 numeric values differ due to integer rounding vs. float precision. Neither file was deleted.

2. **9,028-Row CSV Files**:
   - **Inspected**: Searched the entire repository for 9,028-row datasets. Identified 1 file ([`healthy_foods_database.csv`](file:///Users/kommusaishruthin/Desktop/Infosys/datasets/optional/healthy_foods_database.csv), 9,028 rows × 10 columns).
   - *Result*: Moved to `datasets/optional/` for optional future lookup capabilities.

---

## ⚙️ Git & Licensing Considerations

- **Total Dataset Directory Size**: ~20.9 MB across all 7 CSV files.
- **Max Single File Size**: 16.27 MB (`food_nutrition.csv`), which is comfortably within GitHub's 100 MB per-file push limit.
- **Security Audit**: Verified that no sensitive user data, secrets, or API keys are present in any CSV dataset.
