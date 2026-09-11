# Milestone 2 — Week 3 — Day 13: Data Cleaning Report
**AI Nutrition Intelligence System**

---

## 📌 Executive Summary
This report documents the Day 13 data cleaning process for the Nutritional Deficiency ML Dataset. The original preprocessed CSV ([`datasets/deficiency/deficiency_preprocessed.csv`](file:///Users/kommusaishruthin/Desktop/Infosys/datasets/deficiency/deficiency_preprocessed.csv)) was treated as **READ-ONLY**, validated against biological domain constraints, verified for data integrity, and saved as the clean baseline ([`datasets/deficiency/deficiency_cleaned.csv`](file:///Users/kommusaishruthin/Desktop/Infosys/datasets/deficiency/deficiency_cleaned.csv)).

---

## 📊 Dataset Shape Comparison

| Metric | Original Input Dataset | Cleaned Output Dataset | Variance |
| :--- | :---: | :---: | :---: |
| **Row Count** | 4000 | 4000 | 0 |
| **Column Count** | 49 | 49 | 0 |
| **File Path** | `datasets/deficiency/deficiency_preprocessed.csv` | `datasets/deficiency/deficiency_cleaned.csv` | Output Created |

---

## 🔍 Validation & Data Quality Audit Results

### 1. Missing Values Audit
- **Total Missing Values**: 0 across all 4,000 rows and 49 columns.
- **Finding**: 100% complete dataset. No missing value imputation was required.

### 2. Duplicate Rows Audit
- **Duplicate Rows Found**: 0.
- **Finding**: 100% unique records. No row deletion was necessary.

### 3. Numerical Feature Domain Validation
- **Features Audited**: `age`, `bmi`, `hemoglobin_g_dl`, `serum_vitamin_d_ng_ml`, `serum_vitamin_b12_pg_ml`, `serum_folate_ng_ml`, and 8 RDA percentage features.
- **Invalid Values Found**: 0.
- **Range Audit**:
  - `age`: Min = 18, Max = 84 (Valid adult demographic range)
  - `bmi`: Min = 15.0, Max = 45.0 kg/m² (Valid physiological BMI range)
  - `hemoglobin_g_dl`: Min = 9.6, Max = 18.0 g/dL (Valid clinical hemoglobin range)
  - RDA Percentages: All values non-negative floats.

### 4. Binary / Dummy Column Validation
- **Validated Binary Columns**: 33 binary indicator flags (`gender_*`, `smoking_*`, `alcohol_*`, `exercise_*`, `diet_*`, `sun_*`, `income_*`, `latitude_*`, `has_*`).
- **Validation Result**: 100% compliant. All binary columns contain strictly values `{0, 1}`.

### 5. Target Label Validation (`disease_diagnosis`)
- **Encodings Found**: `[np.int64(0), np.int64(1), np.int64(2), np.int64(3), np.int64(4)]`.
- **Target Mapping Verification**:
  - `0`: **Anemia** (1,245 records / 31.13%)
  - `1`: **Healthy** (1,509 records / 37.73%)
  - `2`: **Night_Blindness** (122 records / 3.05%)
  - `3`: **Rickets_Osteomalacia** (1,029 records / 25.73%)
  - `4`: **Scurvy** (95 records / 2.38%)
- **Target Label Integrity**: Intact. No target re-labeling or mapping modifications were made.

---

## 🧬 Outlier Investigation & Retention Decisions

The Day 12 EDA flagged extreme numerical values in serum laboratory biomarkers and RDA percentages. These outliers were audited using the Interquartile Range (IQR) method ($Q3 + 1.5 \times IQR$):

| Feature | Q3 | IQR | Upper Bound | Max Value | Outlier Count | Outlier % |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| `serum_vitamin_d_ng_ml` | 27.9 | 16.2 | 52.2 | 80.0 | 156 | 3.9% |
| `vitamin_d_percent_rda` | 93.32 | 52.59 | 172.2 | 275.6 | 133 | 3.33% |
| `serum_vitamin_b12_pg_ml` | 338.4 | 217.2 | 664.2 | 1138.1 | 91 | 2.27% |
| `serum_folate_ng_ml` | 13.8 | 6.7 | 23.85 | 25.0 | 71 | 1.77% |


### Outlier Decision Rationale
- **Biological Plausibility**: High serum vitamin D ($> 52.2\text{ ng/mL}$) and high vitamin B12 ($> 664.2\text{ pg/mL}$) correspond to patients receiving clinical vitamin supplementation or high-dose therapy.
- **Clinical Extreme States**: Low values directly correspond to severe pathological states (e.g. Scurvy with Vitamin C RDA $< 25\%$ and Rickets with Serum Vitamin D $< 10\text{ ng/mL}$).
- **Action**: **ALL OUTLIERS WERE RETAINED**. Automatic deletion would remove critical clinical signals for rare deficiency diseases.

---

## 🛠️ Transformations Summary

### Transformations Performed:
1. Validated schema, column data types, missing values, duplicates, domain ranges, and target encodings.
2. Verified 100% data integrity across all 4,000 records and 49 features.
3. Exported validated baseline to `datasets/deficiency/deficiency_cleaned.csv`.

### Transformations NOT Performed (Deferred to Day 14):
1. **SMOTE / Class Resampling**: Deferred to Day 14 feature engineering to avoid data leakage prior to train-test splitting.
2. **Feature Scaling (StandardScaler / RobustScaler)**: Deferred to Day 14 preprocessing pipelines.
3. **Correlation-Based Feature Dropping**: Deferred to Day 14 feature selection.

---

## ✅ Readiness Assessment for Day 14

- [x] Input CSV hash remains unchanged (`True`).
- [x] Cleaned dataset generated at `datasets/deficiency/deficiency_cleaned.csv`.
- [x] Target column remains `disease_diagnosis` with preserved class labels `(0, 1, 2, 3, 4)`.
- [x] Dataset is 100% clean, verified, and ready for Feature Engineering in Day 14.
