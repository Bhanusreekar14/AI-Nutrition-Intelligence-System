import json
import os
import sys
import io
import base64
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.compose import ColumnTransformer
import joblib

notebook_path = 'backend/ml/notebooks/02_deficiency_preprocessing_explained.ipynb'
os.makedirs(os.path.dirname(notebook_path), exist_ok=True)
os.makedirs('backend/ml/artifacts', exist_ok=True)

df = pd.read_csv('datasets/deficiency/deficiency_cleaned.csv')

cells = []
execution_count = 1

def add_md(text):
    cells.append({
        "cell_type": "markdown",
        "metadata": {},
        "source": [line + "\n" for line in text.split("\n")]
    })

def run_and_add_code(code_str):
    global execution_count
    
    old_stdout = sys.stdout
    sys.stdout = buffer = io.StringIO()
    plt.close('all')
    
    exec_globals = {
        'pd': pd,
        'np': np,
        'plt': plt,
        'sns': sns,
        'train_test_split': train_test_split,
        'StandardScaler': StandardScaler,
        'ColumnTransformer': ColumnTransformer,
        'joblib': joblib,
        'df': df.copy()
    }
    
    outputs = []
    
    try:
        exec(code_str, exec_globals)
        stdout_val = buffer.getvalue()
        if stdout_val:
            outputs.append({
                "name": "stdout",
                "output_type": "stream",
                "text": [line + "\n" for line in stdout_val.split("\n")]
            })
            
        figs = [plt.figure(i) for i in plt.get_fignums()]
        for fig in figs:
            buf = io.BytesIO()
            fig.savefig(buf, format='png', bbox_inches='tight', dpi=100)
            buf.seek(0)
            img_b64 = base64.b64encode(buf.read()).decode('utf-8')
            outputs.append({
                "data": {
                    "image/png": img_b64,
                    "text/plain": "<Figure size ...>"
                },
                "metadata": {},
                "output_type": "display_data"
            })
            plt.close(fig)
            
    except Exception as e:
        outputs.append({
            "ename": type(e).__name__,
            "evalue": str(e),
            "output_type": "error",
            "traceback": [str(e)]
        })
    finally:
        sys.stdout = old_stdout
        
    cells.append({
        "cell_type": "code",
        "execution_count": execution_count,
        "metadata": {},
        "outputs": outputs,
        "source": [line + "\n" for line in code_str.strip().split("\n")]
    })
    execution_count += 1

# =============================================================
# 1. Project Objective
# =============================================================
add_md("""# AI Nutrition Intelligence System
## Educational Guide: ML Preprocessing Pipeline Explained
**Milestone 2 — Week 3 — Notebook 02**

---

### 1. Project Objective & Target Mapping

The goal of this ML preprocessing pipeline is to prepare health-profile, dietary RDA, symptom, and laboratory biomarker data to train Machine Learning models that predict a patient's **nutritional deficiency risk**.

#### 🎯 Target Variable
- **Column**: `disease_diagnosis`
- **Type**: Multi-class Classification (5 discrete health outcomes)

#### 🏷️ Target Encoding Mapping
- **`0`**: **Anemia** (Low Hemoglobin / B12 / Iron)
- **`1`**: **Healthy** (Normal laboratory & RDA metrics)
- **`2`**: **Night_Blindness** (Severe Vitamin A deficiency)
- **`3`**: **Rickets_Osteomalacia** (Severe Vitamin D / Calcium deficiency)
- **`4`**: **Scurvy** (Severe Vitamin C deficiency)
""")

# =============================================================
# 2. Import Libraries
# =============================================================
add_md("""### 2. Import Libraries

Before processing data, we import standard Python data science libraries.
""")

code_sec2 = """import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.compose import ColumnTransformer
import joblib
import warnings

warnings.filterwarnings('ignore')
print("✅ All required libraries imported successfully!")
"""
run_and_add_code(code_sec2)

add_md("""#### 📖 What is the purpose of these libraries?
- **Pandas (`pd`)**: For tabular data manipulation, reading CSV files, and DataFrame operations.
- **NumPy (`np`)**: For numerical computations, array manipulation, and mathematical operations.
- **Matplotlib (`plt`) & Seaborn (`sns`)**: For plotting data distributions, correlation heatmaps, and target class visualizations.
- **Scikit-Learn (`sklearn`)**:
  - `train_test_split`: For performing stratified data splitting into training, validation, and testing sets.
  - `StandardScaler`: For standardizing continuous features to mean=0 and variance=1.
  - `ColumnTransformer`: For building modular preprocessing pipelines that handle continuous and categorical features independently.
- **Joblib**: For serializing and saving trained preprocessor objects to disk for deployment.
""")

# =============================================================
# 3. Load Dataset
# =============================================================
add_md("""### 3. Load Dataset

We load the cleaned dataset produced in Day 13 ([`datasets/deficiency/deficiency_cleaned.csv`](file:///Users/kommusaishruthin/Desktop/Infosys/datasets/deficiency/deficiency_cleaned.csv)).
""")

code_sec3 = """dataset_path = 'datasets/deficiency/deficiency_cleaned.csv'
df = pd.read_csv(dataset_path)

print("=== DATASET INSPECTION ===")
print(f"Dataset Shape : {df.shape[0]} rows x {df.shape[1]} columns\\n")
print("--- First 5 Rows ---")
print(df.head(5))

print("\\n--- Data Types Summary ---")
print(df.dtypes.value_counts())
"""
run_and_add_code(code_sec3)

add_md("""#### 📖 Understanding Each Operation:
- **`pd.read_csv()`**: Reads the CSV file from disk into a Pandas DataFrame in RAM.
- **`df.head(5)`**: Displays the top 5 rows to visually inspect feature values.
- **`df.shape`**: Returns a tuple `(rows, columns)` showing dataset dimensions (4,000 × 49).
- **`df.dtypes`**: Summarizes column data types (36 `int64` binary/integer columns and 13 `float64` continuous columns).
""")

# =============================================================
# 4. Understand Feature Groups
# =============================================================
add_md("""### 4. Understand Feature Groups

The 49 columns in our dataset fall into 5 distinct domain feature groups:
""")

code_sec4 = """target_col = 'disease_diagnosis'

demo_cols = [c for c in df.columns if c.startswith(('gender_', 'smoking_', 'alcohol_', 'exercise_', 'diet_', 'sun_', 'income_', 'latitude_')) or c in ['age', 'bmi']]
rda_cols = [c for c in df.columns if c.endswith('_percent_rda')]
lab_cols = ['hemoglobin_g_dl', 'serum_vitamin_d_ng_ml', 'serum_vitamin_b12_pg_ml', 'serum_folate_ng_ml']
symptom_cols = [c for c in df.columns if c.startswith('has_')] + ['symptoms_count']

print("=== FEATURE GROUPS BREAKDOWN ===")
print(f"1. Demographic & Health Profile ({len(demo_cols)} features):\\n   {demo_cols[:5]}...")
print(f"2. Dietary Intake / RDA %      ({len(rda_cols)} features):\\n   {rda_cols}")
print(f"3. Laboratory Biomarkers        ({len(lab_cols)} features):\\n   {lab_cols}")
print(f"4. Clinical Symptoms            ({len(symptom_cols)} features):\\n   {symptom_cols[:5]}...")
print(f"5. Target Outcome               (1 feature) : [{target_col}]")
"""
run_and_add_code(code_sec4)

add_md("""#### 📖 Why Grouping Matters:
Categorizing features allows us to apply domain-specific preprocessing (e.g. standardizing continuous laboratory biomarkers while passing through binary 0/1 symptom indicators without unnecessary scaling).
""")

# =============================================================
# 5. Separate Features ($X$) and Target ($y$)
# =============================================================
add_md("""### 5. Separate Features ($X$) and Target ($y$)

Before splitting data, we isolate our predictor matrix ($X$) from the label vector ($y$).
""")

code_sec5 = """# X contains all 48 input predictor features
X = df.drop(columns=['disease_diagnosis'])

# y contains the target label disease_diagnosis (0-4)
y = df['disease_diagnosis']

print("=== FEATURE & TARGET SEPARATION ===")
print(f"Predictor Matrix (X) Shape : {X.shape[0]} samples x {X.shape[1]} features")
print(f"Target Vector (y) Shape    : {y.shape[0]} samples")
print(f"Class Counts in y          :\\n{y.value_counts().sort_index()}")
"""
run_and_add_code(code_sec5)

add_md("""#### 📖 Core Definitions:
- **$X$ (Feature Matrix)**: The collection of 48 input variables (biomarkers, RDA percentages, symptoms, demographics) that the machine learning algorithm uses to find patterns.
- **$y$ (Target Vector)**: The ground-truth answer that the model is trying to predict (`0: Anemia`, `1: Healthy`, `2: Night_Blindness`, `3: Rickets`, `4: Scurvy`).
""")

# =============================================================
# 6. Train / Validation / Test Split
# =============================================================
add_md("""### 6. Train / Validation / Test Split

We partition the dataset into 3 disjoint subsets using a **Stratified Split**:
- **Training Set (70% = 2,800 samples)**: Used for model learning and parameter optimization.
- **Validation Set (15% = 600 samples)**: Used for hyperparameter tuning and model selection.
- **Test Set (15% = 600 samples)**: Kept completely isolated until final evaluation to provide an unbiased estimate of generalization performance.
""")

code_sec6 = """# First split: 70% Train, 30% Temporary (Validation + Test)
X_train, X_temp, y_train, y_temp = train_test_split(
    X, y, test_size=0.30, random_state=42, stratify=y
)

# Second split: Divide the 30% temp equally into Validation (15%) and Test (15%)
X_val, X_test, y_val, y_test = train_test_split(
    X_temp, y_temp, test_size=0.50, random_state=42, stratify=y_temp
)

print("=== SPLIT SUMMARY ===")
print(f"X_train Shape : {X_train.shape[0]} samples ({X_train.shape[0]/len(X)*100:.1f}%)")
print(f"X_val Shape   : {X_val.shape[0]} samples ({X_val.shape[0]/len(X)*100:.1f}%)")
print(f"X_test Shape  : {X_test.shape[0]} samples ({X_test.shape[0]/len(X)*100:.1f}%)")
"""
run_and_add_code(code_sec6)

add_md("""#### 📖 Why Use Stratification?
Because rare classes like **Night Blindness (3.05%)** and **Scurvy (2.38%)** make up a small portion of the dataset, random unstratified splitting could result in some splits containing almost no minority class samples. `stratify=y` ensures that all 3 splits retain the exact same class proportions as the full dataset.
""")

# =============================================================
# 7. Data Leakage Explanation
# =============================================================
add_md("""### 7. Data Leakage Explanation

> ⚠️ **CRITICAL MACHINE LEARNING PRINCIPLE: AVOID DATA LEAKAGE**

#### What is Data Leakage?
Data leakage occurs when information from outside the training dataset (such as validation or test data statistics) is inadvertently used to fit preprocessing transformations (e.g. mean, standard deviation, or scaling parameters).

#### How We Prevent Data Leakage:
1. **Split First, Fit Later**: We split the dataset into `X_train`, `X_val`, and `X_test` **BEFORE** applying any scaling or feature transformations.
2. **Fit Only on $X_{train}$**: All transformers (such as `StandardScaler`) compute their parameters ($\mu, \sigma$) using **only** `X_train`.
3. **Transform $X_{val}$ and $X_{test}$**: Validation and test sets are transformed using the parameters learned from `X_train`. We **never** call `.fit()` or `.fit_transform()` on validation or test data.
""")

# =============================================================
# 8. Numerical Feature Processing
# =============================================================
add_md("""### 8. Numerical Feature Processing

We identify continuous numerical features (`age`, `bmi`, lab biomarkers, RDA percentages).
""")

code_sec8 = """continuous_cols = [
    'age', 'bmi', 'vitamin_a_percent_rda', 'vitamin_c_percent_rda',
    'vitamin_d_percent_rda', 'vitamin_e_percent_rda', 'vitamin_b12_percent_rda',
    'folate_percent_rda', 'calcium_percent_rda', 'iron_percent_rda',
    'hemoglobin_g_dl', 'serum_vitamin_d_ng_ml', 'serum_vitamin_b12_pg_ml',
    'serum_folate_ng_ml', 'symptoms_count'
]

scaler = StandardScaler()
# Fit scaler ONLY on training data
scaler.fit(X_train[continuous_cols])

# Transform training and validation sets
X_train_scaled_num = scaler.transform(X_train[continuous_cols])
X_val_scaled_num = scaler.transform(X_val[continuous_cols])

print("=== SCALER PARAMS LEARNED FROM X_TRAIN (Sample) ===")
print("Mean values learned for first 5 features:")
for col, mu in zip(continuous_cols[:5], scaler.mean_[:5]):
    print(f" - {col:<25}: mean = {mu:.2f}")
"""
run_and_add_code(code_sec8)

add_md("""#### 📖 Is Scaling Required for Random Forest?
- **Random Forest Baseline**: Tree-based models (Random Forest, Decision Trees, XGBoost) split data based on rank order thresholds ($X_j \le \theta$). They are **monotonically scale-invariant**, meaning feature scaling does not alter decision tree splits or model performance.
- **Why We Still Create Scalers**: Distance-based models (KNN, SVM) and gradient-based models (Logistic Regression, Neural Networks) require scaling. Demonstrating `StandardScaler` prepares our pipeline for multi-model comparison in Day 15 while keeping the baseline pipeline clean.
""")

# =============================================================
# 9. Categorical / Binary Features
# =============================================================
add_md("""### 9. Categorical & Binary Features

We inspect the binary dummy indicators in our dataset.
""")

code_sec9 = """binary_cols = [c for c in X.columns if c not in continuous_cols]

print(f"Binary Features Count: {len(binary_cols)}")
print("Sample Binary Features:")
print(binary_cols[:10])
"""
run_and_add_code(code_sec9)

add_md("""#### 📖 Why No Re-Encoding is Necessary:
All 33 binary features (such as `gender_Female`, `diet_type_Vegan`, `has_fatigue`) are already encoded as discrete numerical flags ($0$ or $1$). Re-applying One-Hot Encoding or Label Encoding would be redundant and unnecessary. They are passed through directly (`passthrough`).
""")

# =============================================================
# 10. Class Imbalance
# =============================================================
add_md("""### 10. Target Class Imbalance Across Splits

We verify target class distributions across the train, validation, and test splits.
""")

code_sec10 = """train_dist = y_train.value_counts(normalize=True).sort_index() * 100
val_dist = y_val.value_counts(normalize=True).sort_index() * 100
test_dist = y_test.value_counts(normalize=True).sort_index() * 100

dist_df = pd.DataFrame({
    'Disease Name': ['Anemia (0)', 'Healthy (1)', 'Night_Blindness (2)', 'Rickets_Osteomalacia (3)', 'Scurvy (4)'],
    'Train (%)': train_dist.values.round(2),
    'Validation (%)': val_dist.values.round(2),
    'Test (%)': test_dist.values.round(2)
})

print("=== STRATIFIED CLASS DISTRIBUTION ACROSS SPLITS ===")
print(dist_df.to_string(index=False))
"""
run_and_add_code(code_sec10)

add_md("""#### 📖 Managing Class Imbalance:
- **Observed Minority Classes**: Night Blindness (3.05%) and Scurvy (2.38%) have low sample counts.
- **Handling Strategy for Random Forest**: Rather than synthesizing artificial data prior to baseline evaluation, we use `class_weight='balanced'` in Random Forest. This weights loss inversely proportional to class frequencies without distorting clinical biomarker distributions.
- **SMOTE Note**: If SMOTE oversampling is evaluated, it must **ONLY be applied to $X_{train}$** to prevent synthetic data from leaking into evaluation sets.
""")

# =============================================================
# 11. Correlation & Feature Selection
# =============================================================
add_md("""### 11. Correlation & Feature Selection Strategy

During Day 12 EDA, strong linear correlations were identified between dietary intakes and serum lab biomarkers:
- `vitamin_d_percent_rda` $\longleftrightarrow$ `serum_vitamin_d_ng_ml` ($r = 0.936$)
- `vitamin_b12_percent_rda` $\longleftrightarrow$ `serum_vitamin_b12_pg_ml` ($r = 0.893$)
- `folate_percent_rda` $\longleftrightarrow$ `serum_folate_ng_ml` ($r = 0.887$)

#### 📖 Why We Do NOT Blindly Delete Correlated Features:
1. **Clinical Complementarity**: Dietary RDA % measures daily intake, while serum level measures physiological storage. A patient may take high oral Vitamin D (high RDA %) but have low serum absorption due to malabsorption disorders.
2. **Tree-Based Resilience**: Random Forest randomly selects feature subsets at each split, naturally mitigating multicollinearity without suffering matrix inversion instability.
""")

# =============================================================
# 12. Reusable Preprocessing Pipeline
# =============================================================
add_md("""### 12. Reusable Scikit-Learn Preprocessing Pipeline

We assemble a clean, production-ready `ColumnTransformer` using Scikit-Learn.
""")

code_sec12 = """preprocessor = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), continuous_cols),
        ('bin', 'passthrough', binary_cols)
    ]
)

# Fit preprocessor strictly on training data
X_train_processed = preprocessor.fit_transform(X_train)

# Transform validation and test data
X_val_processed = preprocessor.transform(X_val)
X_test_processed = preprocessor.transform(X_test)

print("=== PREPROCESSING PIPELINE EXECUTED ===")
print(f"X_train_processed Shape : {X_train_processed.shape}")
print(f"X_val_processed Shape   : {X_val_processed.shape}")
print(f"X_test_processed Shape  : {X_test_processed.shape}")
"""
run_and_add_code(code_sec12)

add_md("""#### 📖 Understanding `.fit()` vs `.transform()`:
- **`.fit()`**: Learns scaling parameters (means $\mu$ and standard deviations $\sigma$) from $X_{train}$.
- **`.transform()`**: Applies the learned parameters to scale datasets ($X_{train}$, $X_{val}$, $X_{test}$).
- **Inference Consistency**: In production (e.g. FastAPI backend), new single-patient prediction requests pass through this exact fitted pipeline.
""")

# =============================================================
# 13. Save Preprocessing Artifacts
# =============================================================
add_md("""### 13. Save Preprocessing Artifacts

We serialize the fitted `ColumnTransformer` pipeline using `joblib`.
""")

code_sec13 = """artifact_path = 'backend/ml/artifacts/preprocessor.joblib'
joblib.dump(preprocessor, artifact_path)

print(f"✅ Preprocessor artifact successfully saved to: {artifact_path}")
print(f"   Artifact File Size: {os.path.getsize(artifact_path) / 1024:.2f} KB")
"""
run_and_add_code(code_sec13)

add_md("""#### 📖 What is `preprocessor.joblib` used for?
When a user submits health information via the web app (e.g. age, dietary logs, symptoms), the FastAPI backend loads `preprocessor.joblib` and calls `.transform()` on the input data before handing it to the ML model for prediction.
""")

# =============================================================
# 14. Final Dataset Summary
# =============================================================
add_md("""### 14. Final Preprocessing Dataset Summary

A summary of all preprocessed dataset splits ready for model training in Day 14.
""")

code_sec14 = """summary_table = pd.DataFrame({
    'Split Name': ['Training Set (X_train, y_train)', 'Validation Set (X_val, y_val)', 'Test Set (X_test, y_test)'],
    'Sample Count': [X_train.shape[0], X_val.shape[0], X_test.shape[0]],
    'Proportion (%)': ['70.0%', '15.0%', '15.0%'],
    'Feature Columns': [X_train.shape[1], X_val.shape[1], X_test.shape[1]],
    'Target Classes': ['0, 1, 2, 3, 4', '0, 1, 2, 3, 4', '0, 1, 2, 3, 4']
})

print("=== FINAL DATASET SUMMARY ===")
print(summary_table.to_string(index=False))
"""
run_and_add_code(code_sec14)

# =============================================================
# 15. Viva / Presentation Explanation Guide
# =============================================================
add_md("""### 15. How I Explain My Preprocessing in Viva

Here is a concise, memorizable 7-point summary to explain this preprocessing pipeline during a project viva or technical presentation:

1. **Clean Baseline Input**: I started with the cleaned 4,000-row × 49-column deficiency dataset ([`datasets/deficiency/deficiency_cleaned.csv`](file:///Users/kommusaishruthin/Desktop/Infosys/datasets/deficiency/deficiency_cleaned.csv)).
2. **Feature & Target Separation**: I separated the 48 predictor variables ($X$) from the multi-class target variable ($y = \text{disease\_diagnosis}$).
3. **Stratified Data Splitting**: I used a **70% Train / 15% Validation / 15% Test** stratified split to preserve minority class proportions (Night Blindness: 3.05%, Scurvy: 2.38%) across all subsets.
4. **Data Leakage Prevention**: I strictly fitted preprocessing transformers **only on training data** ($X_{train}$) and transformed validation and test sets using those learned parameters.
5. **Selective Feature Scaling**: I configured `StandardScaler` for continuous numerical features (age, BMI, biomarkers, RDA percentages) while passing through already-encoded 0/1 binary features without unnecessary scaling.
6. **Class Imbalance Strategy**: I addressed class imbalance using `class_weight='balanced'` for tree-based models, preserving genuine clinical biomarker distributions.
7. **Production Pipeline Serialization**: I exported the fitted `ColumnTransformer` as `backend/ml/artifacts/preprocessor.joblib` for inference integration in the FastAPI backend.

---
**Verification**: Original CSV files, project application code, and database schema remained 100% unchanged.
""")

nb_json = {
    "cells": cells,
    "metadata": {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3"
        },
        "language_info": {
            "name": "python",
            "version": "3.12.0"
        }
    },
    "nbformat": 4,
    "nbformat_minor": 2
}

with open(notebook_path, 'w') as f:
    json.dump(nb_json, f, indent=2)

print(f"Successfully generated educational notebook at: {notebook_path}")
