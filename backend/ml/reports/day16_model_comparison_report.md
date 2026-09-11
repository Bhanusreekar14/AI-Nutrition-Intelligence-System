# Day 16: Model Comparison Report — Random Forest vs XGBoost
**AI Nutrition Intelligence System**

---

## 📌 1. Objective
This report details the empirical comparison between **Random Forest Baseline** (Bagging) and **XGBoost Baseline** (Gradient Boosting) for multi-class nutritional deficiency risk prediction (`disease_diagnosis`).

---

## 📊 2. Dataset & Target Mapping
- **Dataset**: [`datasets/deficiency/deficiency_cleaned.csv`](file:///Users/kommusaishruthin/Desktop/Infosys/datasets/deficiency/deficiency_cleaned.csv) (4,000 rows × 49 columns)
- **Target Mapping**:
  - `0`: **Anemia** (1,245 cases / 31.13%)
  - `1`: **Healthy** (1,509 cases / 37.73%)
  - `2`: **Night_Blindness** (122 cases / 3.05%)
  - `3`: **Rickets_Osteomalacia** (1,029 cases / 25.73%)
  - `4`: **Scurvy** (95 cases / 2.38%)

---

## ✂️ 3. Preprocessing & Stratified Splitting
- **Preprocessor Artifact**: [`backend/ml/artifacts/preprocessor.joblib`](file:///Users/kommusaishruthin/Desktop/Infosys/backend/ml/artifacts/preprocessor.joblib)
- **Split Strategy**: 70% Train (2,800), 15% Val (600), 15% Test (600) — Stratified, `random_state=42`.

---

## ⚙️ 4. Model Configurations
- **Random Forest Baseline**: `RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced')`
- **XGBoost Baseline**: `XGBClassifier(objective='multi:softprob', num_class=5, n_estimators=300, max_depth=6, learning_rate=0.05, subsample=0.8, colsample_bytree=0.8, random_state=42)`

---

## 📈 5. Empirical Performance Comparison Table

| Model | Dataset | Accuracy | Precision (W) | Recall (W) | Weighted F1 | Macro F1 | ROC-AUC (OvR) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Random Forest** | **Validation** | 0.9800 | 0.9805 | 0.9800 | 0.9799 | 0.9644 | 0.9991 |
| **Random Forest** | **Test** | 0.9767 | 0.9770 | 0.9767 | 0.9767 | 0.9682 | 0.9994 |
| **XGBoost** | **Validation** | **0.9983** | **0.9984** | **0.9983** | **0.9984** | **0.9925** | **1.0000** |
| **XGBoost** | **Test** | **0.9917** | **0.9916** | **0.9917** | **0.9916** | **0.9801** | **1.0000** |

---

## 🧬 6. Minority Class Performance Comparison (Test Set)

| Model | Class | Precision | Recall | F1-Score | Support |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **Random Forest** | **Night_Blindness** | 0.9500 | 0.9500 | 0.9500 | 19 |
| **XGBoost** | **Night_Blindness** | 0.9444 | 0.8947 | 0.9189 | 19 |
| **Random Forest** | **Scurvy** | 1.0000 | 0.9286 | 0.9630 | 14 |
| **XGBoost** | **Scurvy** | **1.0000** | **1.0000** | **1.0000** | 14 |

---

## 🔝 7. Top 10 XGBoost Feature Importances

| Rank | Feature Name | Importance Weight |
| :---: | :--- | :---: |
| 1 | `symptoms_count` | 0.2054 (20.54%) |
| 2 | `vitamin_c_percent_rda` | 0.0990 (9.90%) |
| 3 | `has_bleeding_gums` | 0.0863 (8.63%) |
| 4 | `has_night_blindness` | 0.0848 (8.48%) |
| 5 | `vitamin_a_percent_rda` | 0.0828 (8.28%) |
| 6 | `has_fatigue` | 0.0526 (5.26%) |
| 7 | `vitamin_d_percent_rda` | 0.0466 (4.66%) |
| 8 | `sun_exposure_High` | 0.0383 (3.83%) |
| 9 | `vitamin_b12_percent_rda` | 0.0291 (2.91%) |
| 10 | `sun_exposure_Low` | 0.0238 (2.38%) |


---

## 🏆 8. Selected Top-Performing Model & Justification

**Selected Model**: **XGBoost Baseline** ([`backend/ml/artifacts/xgboost_baseline.joblib`](file:///Users/kommusaishruthin/Desktop/Infosys/backend/ml/artifacts/xgboost_baseline.joblib))

### Rationale:
1. **Superior Accuracy**: XGBoost achieved **99.17% Test Accuracy** vs **97.67%** for Random Forest.
2. **Superior Macro F1**: XGBoost achieved **0.9801 Macro F1** vs **0.9682** for Random Forest.
3. **Perfect Scurvy Recall**: XGBoost achieved **100% (14/14)** Recall on Scurvy (vs 92.9% for RF).
4. **Near-Perfect ROC-AUC**: XGBoost achieved **1.0000 ROC-AUC** across validation and test sets.

---

## 📝 9. Limitations & Conclusion
- **Clinical Disclaimer**: "This model provides prediction/risk-support information and is not a medical diagnosis."
- **Readiness**: XGBoost artifact is saved and ready for Day 17 hyperparameter optimization / SHAP analysis.
