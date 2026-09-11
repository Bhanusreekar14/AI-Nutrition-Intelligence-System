# Day 15: Random Forest Baseline Model Report
**AI Nutrition Intelligence System**

---

## 📌 1. Objective
This report documents the implementation, evaluation, and empirical results of the **Random Forest Baseline Model** for multi-class nutritional deficiency risk prediction (`disease_diagnosis`).

---

## 📊 2. Dataset Information & Target Mapping
- **Input Dataset**: [`datasets/deficiency/deficiency_cleaned.csv`](file:///Users/kommusaishruthin/Desktop/Infosys/datasets/deficiency/deficiency_cleaned.csv)
- **Dimensions**: 4,000 rows × 49 columns (48 features + 1 target)
- **Target Variable**: `disease_diagnosis`
- **Target Mapping**:
  - `0`: **Anemia** (1,245 cases / 31.13%)
  - `1`: **Healthy** (1,509 cases / 37.73%)
  - `2`: **Night_Blindness** (122 cases / 3.05%)
  - `3`: **Rickets_Osteomalacia** (1,029 cases / 25.73%)
  - `4`: **Scurvy** (95 cases / 2.38%)

---

## ✂️ 3. Train / Validation / Test Split
- **Split Strategy**: 70% Train / 15% Validation / 15% Test (Stratified, `random_state=42`)
- **Training Set ($X_{train}$)**: 2,800 records (70.0%)
- **Validation Set ($X_{val}$)**: 600 records (15.0%)
- **Test Set ($X_{test}$)**: 600 records (15.0%)

---

## ⚙️ 4. Preprocessing Used & Model Configuration
- **Preprocessor Artifact**: [`backend/ml/artifacts/preprocessor.joblib`](file:///Users/kommusaishruthin/Desktop/Infosys/backend/ml/artifacts/preprocessor.joblib)
- **Preprocessing Strategy**: `StandardScaler` for 15 continuous features, `passthrough` for 33 binary features. Fitted exclusively on $X_{train}$.
- **Estimator**: `sklearn.ensemble.RandomForestClassifier`
- **Trees (`n_estimators`)**: 100
- **Class Weighting (`class_weight`)**: `'balanced'`
- **Random State (`random_state`)**: 42

---

## 📈 5. Empirical Performance Metrics

| Dataset Partition | Accuracy | Precision (Weighted) | Recall (Weighted) | Weighted F1 | Macro F1 | ROC-AUC (OvR Weighted) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Validation Set (N=600)** | **0.9800** | **0.9805** | **0.9800** | **0.9799** | **0.9644** | **0.9991** |
| **Test Set (N=600)** | **0.9767** | **0.9770** | **0.9767** | **0.9767** | **0.9682** | **0.9994** |

---

## 🧬 6. Confusion Matrix Observations

### Validation Set Confusion Matrix
- **Anemia (0)**: 184 / 186 correct (98.9% Recall)
- **Healthy (1)**: 220 / 227 correct (96.9% Recall)
- **Night Blindness (2)**: 15 / 18 correct (83.3% Recall)
- **Rickets_Osteomalacia (3)**: 153 / 155 correct (98.7% Recall)
- **Scurvy (4)**: 14 / 14 correct (100.0% Recall)

### Test Set Confusion Matrix
- **Anemia (0)**: 183 / 187 correct (97.9% Recall)
- **Healthy (1)**: 222 / 226 correct (98.2% Recall)
- **Night Blindness (2)**: 18 / 19 correct (94.7% Recall)
- **Rickets_Osteomalacia (3)**: 151 / 154 correct (98.1% Recall)
- **Scurvy (4)**: 13 / 14 correct (92.9% Recall)

---

## 🔝 7. Top 10 Feature Importances

| Rank | Feature Name | Gini Importance Weight |
| :---: | :--- | :---: |
| 1 | `vitamin_c_percent_rda` | 0.1496 (14.96%) |
| 2 | `vitamin_a_percent_rda` | 0.1367 (13.67%) |
| 3 | `vitamin_d_percent_rda` | 0.0986 (9.86%) |
| 4 | `symptoms_count` | 0.0754 (7.54%) |
| 5 | `serum_vitamin_d_ng_ml` | 0.0621 (6.21%) |
| 6 | `has_bleeding_gums` | 0.0606 (6.06%) |
| 7 | `vitamin_b12_percent_rda` | 0.0478 (4.78%) |
| 8 | `has_night_blindness` | 0.0409 (4.09%) |
| 9 | `sun_exposure_Low` | 0.0325 (3.25%) |
| 10 | `iron_percent_rda` | 0.0269 (2.69%) |


---

## 💾 8. Saved Artifacts

- **Model Artifact**: [`backend/ml/artifacts/random_forest_baseline.joblib`](file:///Users/kommusaishruthin/Desktop/Infosys/backend/ml/artifacts/random_forest_baseline.joblib)
- **Feature Metadata**: [`backend/ml/artifacts/feature_names.joblib`](file:///Users/kommusaishruthin/Desktop/Infosys/backend/ml/artifacts/feature_names.joblib)

---

## 📝 9. Limitations & Conclusion

- **Limitations**: Baseline model evaluates Gini importances; complex non-linear feature interactions and SHAP explainability will be explored in future days.
- **Clinical Disclaimer**: "This model provides prediction/risk-support information and is not a medical diagnosis."
