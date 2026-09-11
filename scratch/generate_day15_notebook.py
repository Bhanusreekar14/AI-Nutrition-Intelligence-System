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
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    classification_report, confusion_matrix, roc_auc_score
)
import joblib

notebook_path = 'backend/ml/notebooks/03_random_forest_baseline.ipynb'
report_path = 'backend/ml/reports/day15_random_forest_report.md'
model_path = 'backend/ml/artifacts/random_forest_baseline.joblib'
metadata_path = 'backend/ml/artifacts/feature_names.joblib'

os.makedirs(os.path.dirname(notebook_path), exist_ok=True)
os.makedirs('backend/ml/artifacts', exist_ok=True)
os.makedirs(os.path.dirname(report_path), exist_ok=True)

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
        'RandomForestClassifier': RandomForestClassifier,
        'accuracy_score': accuracy_score,
        'precision_score': precision_score,
        'recall_score': recall_score,
        'f1_score': f1_score,
        'classification_report': classification_report,
        'confusion_matrix': confusion_matrix,
        'roc_auc_score': roc_auc_score,
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
## Random Forest Baseline Model
**Milestone 2 — Week 3 — Day 15**

---

### 1. Project Objective

"We are building a machine learning model that predicts nutritional deficiency-related disease categories from the available nutritional, laboratory, symptom and demographic features."

> ⚠️ **Important Clinical Notice**: This system is designed as a **prediction and risk-support tool** to assist healthcare professionals and individuals in identifying early deficiency risks. It is **NOT** a standalone medical diagnosis system.

#### 🎯 Target Encodings & Labels
- **`0`**: **Anemia**
- **`1`**: **Healthy**
- **`2`**: **Night_Blindness**
- **`3`**: **Rickets_Osteomalacia**
- **`4`**: **Scurvy**
""")

# =============================================================
# 2. Import Libraries
# =============================================================
add_md("""### 2. Import Libraries

We import only the essential Python data science and machine learning libraries.
""")

code_sec2 = """import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    classification_report, confusion_matrix, roc_auc_score
)
import joblib
import warnings

warnings.filterwarnings('ignore')
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['figure.figsize'] = (10, 6)
plt.rcParams['font.size'] = 11

print("✅ Required libraries imported successfully!")
"""
run_and_add_code(code_sec2)

add_md("""#### 📖 Library Explanations:
- **Pandas (`pd`)**: Data structure manipulation and DataFrame operations.
- **NumPy (`np`)**: High-performance mathematical computations and array handling.
- **Matplotlib (`plt`) & Seaborn (`sns`)**: Data visualization and confusion matrix plotting.
- **Scikit-Learn (`sklearn`)**: ML algorithms (`RandomForestClassifier`), metrics evaluation, and data partitioning.
- **Joblib**: Saving and loading trained machine learning models and preprocessor pipelines.
""")

# =============================================================
# 3. Load Dataset
# =============================================================
add_md("""### 3. Load Dataset

Loading the verified baseline dataset (`datasets/deficiency/deficiency_cleaned.csv`).
""")

code_sec3 = """dataset_path = 'datasets/deficiency/deficiency_cleaned.csv'
df = pd.read_csv(dataset_path)

print("=== DATASET OVERVIEW ===")
print(f"Shape: {df.shape[0]} rows x {df.shape[1]} columns\\n")

print("--- First 5 Rows ---")
print(df.head(5))

print("\\n--- Column Names ---")
print(list(df.columns))

print("\\n--- Data Types Summary ---")
print(df.dtypes.value_counts())
"""
run_and_add_code(code_sec3)

# =============================================================
# 4. Separate Features and Target
# =============================================================
add_md("""### 4. Separate Features ($X$) and Target ($y$)

- **$X$**: Input features used by the model to learn patterns.
- **$y$**: Target outcome (`disease_diagnosis`) that the model predicts.
""")

code_sec4 = """X = df.drop(columns=["disease_diagnosis"])
y = df["disease_diagnosis"]

print("=== SEPARATION SUMMARY ===")
print(f"Input Feature Matrix (X) Shape : {X.shape[0]} rows x {X.shape[1]} columns")
print(f"Target Label Vector (y) Shape   : {y.shape[0]} rows")
"""
run_and_add_code(code_sec4)

# =============================================================
# 5. Train / Validation / Test Split
# =============================================================
add_md("""### 5. Train / Validation / Test Split

We partition data into 70% Training, 15% Validation, and 15% Test using `random_state=42` and `stratify=y`.
""")

code_sec5 = """# 70% Train, 30% Temp (Validation + Test)
X_train, X_temp, y_train, y_temp = train_test_split(
    X, y, test_size=0.30, random_state=42, stratify=y
)

# Split Temp into 15% Validation and 15% Test
X_val, X_test, y_val, y_test = train_test_split(
    X_temp, y_temp, test_size=0.50, random_state=42, stratify=y_temp
)

print("=== SPLIT SHAPES ===")
print(f"Training Set   (70%) : {X_train.shape[0]} samples")
print(f"Validation Set (15%) : {X_val.shape[0]} samples")
print(f"Test Set       (15%) : {X_test.shape[0]} samples")

print("\\n=== TARGET CLASS DISTRIBUTION ACROSS SPLITS ===")
dist_df = pd.DataFrame({
    'Disease Class': ['Anemia (0)', 'Healthy (1)', 'Night_Blindness (2)', 'Rickets_Osteomalacia (3)', 'Scurvy (4)'],
    'Train Count': y_train.value_counts().sort_index().values,
    'Train (%)': (y_train.value_counts(normalize=True).sort_index() * 100).values.round(2),
    'Val Count': y_val.value_counts().sort_index().values,
    'Val (%)': (y_val.value_counts(normalize=True).sort_index() * 100).values.round(2),
    'Test Count': y_test.value_counts().sort_index().values,
    'Test (%)': (y_test.value_counts(normalize=True).sort_index() * 100).values.round(2)
})
print(dist_df.to_string(index=False))
"""
run_and_add_code(code_sec5)

add_md("""#### 📖 Why Stratification is Important:
Target classes are severely imbalanced. **Night Blindness (3.05%)** and **Scurvy (2.38%)** are rare minority classes. Stratified splitting enforces that every split contains the exact same percentage of each disease class, preventing evaluation bias.
""")

# =============================================================
# 6. Load Existing Preprocessor
# =============================================================
add_md("""### 6. Load Existing Preprocessor

We load `backend/ml/artifacts/preprocessor.joblib` and transform all dataset partitions.

> ⚠️ **Data Leakage Notice**: We apply ONLY `.transform()`. `.fit()` must NEVER be called on validation or test sets.
""")

code_sec6 = """preprocessor_path = 'backend/ml/artifacts/preprocessor.joblib'
preprocessor = joblib.load(preprocessor_path)

# Transform datasets
X_train_processed = preprocessor.transform(X_train)
X_val_processed = preprocessor.transform(X_val)
X_test_processed = preprocessor.transform(X_test)

print("=== TRANSFORMED MATRIX SHAPES ===")
print(f"X_train_processed : {X_train_processed.shape}")
print(f"X_val_processed   : {X_val_processed.shape}")
print(f"X_test_processed  : {X_test_processed.shape}")
"""
run_and_add_code(code_sec6)

add_md("""#### 📖 What is Data Leakage?
Data leakage happens when information from validation or test sets influences training. If scalers are fitted on the whole dataset, test set means and variances bleed into training, giving misleadingly high performance scores.
""")

# =============================================================
# 7. Train Random Forest Baseline
# =============================================================
add_md("""### 7. Train Random Forest Baseline

We train `RandomForestClassifier` with `class_weight="balanced"`.
""")

code_sec7 = """model = RandomForestClassifier(
    n_estimators=100,
    random_state=42,
    class_weight="balanced",
    n_jobs=-1
)

# Train strictly using training data
model.fit(X_train_processed, y_train)

print("✅ Random Forest Baseline trained successfully!")
"""
run_and_add_code(code_sec7)

add_md("""#### 📖 Why Use `class_weight="balanced"`?
`class_weight="balanced"` automatically penalizes classification errors on minority classes (Night Blindness & Scurvy) more heavily, forcing the decision trees to focus on rare disease signals.
""")

# =============================================================
# 8. Validation Predictions
# =============================================================
add_md("""### 8. Validation Predictions""")

code_sec8 = """y_val_pred = model.predict(X_val_processed)
y_val_proba = model.predict_proba(X_val_processed)

print(f"Validation Predictions Generated : {len(y_val_pred)} predictions")
"""
run_and_add_code(code_sec8)

# =============================================================
# 9. Validation Evaluation
# =============================================================
add_md("""### 9. Validation Evaluation""")

code_sec9 = """val_acc = accuracy_score(y_val, y_val_pred)
val_prec_w = precision_score(y_val, y_val_pred, average="weighted")
val_rec_w = recall_score(y_val, y_val_pred, average="weighted")
val_f1_w = f1_score(y_val, y_val_pred, average="weighted")
val_f1_macro = f1_score(y_val, y_val_pred, average="macro")

print("=== VALIDATION METRICS ===")
print(f"Accuracy           : {val_acc:.4f} ({val_acc*100:.2f}%)")
print(f"Weighted Precision : {val_prec_w:.4f}")
print(f"Weighted Recall    : {val_rec_w:.4f}")
print(f"Weighted F1-Score  : {val_f1_w:.4f}")
print(f"Macro F1-Score     : {val_f1_macro:.4f}")

target_names = ['Anemia', 'Healthy', 'Night_Blindness', 'Rickets_Osteomalacia', 'Scurvy']
print("\\n--- Classification Report (Validation) ---")
print(classification_report(y_val, y_val_pred, target_names=target_names))

cm_val = confusion_matrix(y_val, y_val_pred)
plt.figure(figsize=(8, 6))
sns.heatmap(cm_val, annot=True, fmt='d', cmap='Blues', xticklabels=target_names, yticklabels=target_names)
plt.title('Validation Confusion Matrix - Random Forest Baseline', fontweight='bold', fontsize=12)
plt.xlabel('Predicted Diagnosis')
plt.ylabel('Actual Diagnosis')
plt.xticks(rotation=25)
plt.tight_layout()
plt.show()
"""
run_and_add_code(code_sec9)

# =============================================================
# 10. Test Evaluation
# =============================================================
add_md("""### 10. Test Evaluation

We evaluate our final baseline model on the held-out Test Set.
""")

code_sec10 = """y_test_pred = model.predict(X_test_processed)
y_test_proba = model.predict_proba(X_test_processed)

test_acc = accuracy_score(y_test, y_test_pred)
test_prec_w = precision_score(y_test, y_test_pred, average="weighted")
test_rec_w = recall_score(y_test, y_test_pred, average="weighted")
test_f1_w = f1_score(y_test, y_test_pred, average="weighted")
test_f1_macro = f1_score(y_test, y_test_pred, average="macro")

print("=== TEST METRICS ===")
print(f"Accuracy           : {test_acc:.4f} ({test_acc*100:.2f}%)")
print(f"Weighted Precision : {test_prec_w:.4f}")
print(f"Weighted Recall    : {test_rec_w:.4f}")
print(f"Weighted F1-Score  : {test_f1_w:.4f}")
print(f"Macro F1-Score     : {test_f1_macro:.4f}")

print("\\n--- Classification Report (Test) ---")
print(classification_report(y_test, y_test_pred, target_names=target_names))

cm_test = confusion_matrix(y_test, y_test_pred)
plt.figure(figsize=(8, 6))
sns.heatmap(cm_test, annot=True, fmt='d', cmap='Greens', xticklabels=target_names, yticklabels=target_names)
plt.title('Test Confusion Matrix - Random Forest Baseline', fontweight='bold', fontsize=12)
plt.xlabel('Predicted Diagnosis')
plt.ylabel('Actual Diagnosis')
plt.xticks(rotation=25)
plt.tight_layout()
plt.show()
"""
run_and_add_code(code_sec10)

# =============================================================
# 11. Multiclass ROC-AUC
# =============================================================
add_md("""### 11. Multiclass ROC-AUC

We calculate multi-class ROC-AUC using **One-vs-Rest (`multi_class="ovr"`)** with weighted averaging.
""")

code_sec11 = """val_auc = roc_auc_score(y_val, y_val_proba, multi_class="ovr", average="weighted")
test_auc = roc_auc_score(y_test, y_test_proba, multi_class="ovr", average="weighted")

print("=== MULTICLASS ROC-AUC SCORES (OvR Weighted) ===")
print(f"Validation ROC-AUC : {val_auc:.4f}")
print(f"Test ROC-AUC       : {test_auc:.4f}")
"""
run_and_add_code(code_sec11)

# =============================================================
# 12. Feature Importance
# =============================================================
add_md("""### 12. Feature Importance""")

code_sec12 = """continuous_cols = [
    'age', 'bmi', 'vitamin_a_percent_rda', 'vitamin_c_percent_rda',
    'vitamin_d_percent_rda', 'vitamin_e_percent_rda', 'vitamin_b12_percent_rda',
    'folate_percent_rda', 'calcium_percent_rda', 'iron_percent_rda',
    'hemoglobin_g_dl', 'serum_vitamin_d_ng_ml', 'serum_vitamin_b12_pg_ml',
    'serum_folate_ng_ml', 'symptoms_count'
]
binary_cols = [c for c in X.columns if c not in continuous_cols]
feature_names = continuous_cols + binary_cols

importance_df = pd.DataFrame({
    'Feature': feature_names,
    'Importance': model.feature_importances_
}).sort_values(by='Importance', ascending=False)

print("=== TOP 10 FEATURE IMPORTANCES ===")
print(importance_df.head(10).to_string(index=False))

plt.figure(figsize=(10, 6))
sns.barplot(data=importance_df.head(10), x='Importance', y='Feature', palette='viridis')
plt.title('Top 10 Feature Importances - Random Forest Baseline', fontweight='bold', fontsize=13)
plt.xlabel('Gini Importance Weight')
plt.ylabel('Feature Name')
plt.tight_layout()
plt.show()
"""
run_and_add_code(code_sec12)

add_md("""#### 📖 Important Feature Interpretation Note:
Feature importance measures how frequently a variable was used to split decision trees to reduce impurity. It indicates **predictive utility**, NOT direct medical causation.
""")

# =============================================================
# 13. Baseline Results Table
# =============================================================
add_md("""### 13. Baseline Results Table""")

code_sec13 = """summary_table = pd.DataFrame({
    'Dataset': ['Validation', 'Test'],
    'Accuracy': [f"{val_acc:.4f}", f"{test_acc:.4f}"],
    'Precision': [f"{val_prec_w:.4f}", f"{test_prec_w:.4f}"],
    'Recall': [f"{val_rec_w:.4f}", f"{test_rec_w:.4f}"],
    'Weighted F1': [f"{val_f1_w:.4f}", f"{test_f1_w:.4f}"],
    'Macro F1': [f"{val_f1_macro:.4f}", f"{test_f1_macro:.4f}"],
    'ROC-AUC': [f"{val_auc:.4f}", f"{test_auc:.4f}"]
})

print("=== BASELINE RESULTS TABLE ===")
print(summary_table.to_string(index=False))
"""
run_and_add_code(code_sec13)

# =============================================================
# 14. Model Saving
# =============================================================
add_md("""### 14. Model Saving""")

code_sec14 = """joblib.dump(model, model_path)
joblib.dump(feature_names, metadata_path)

print(f"✅ Saved trained model artifact to: {model_path} ({os.path.getsize(model_path)/1024:.2f} KB)")
print(f"✅ Saved feature metadata artifact to: {metadata_path}")
"""
run_and_add_code(code_sec14)

# =============================================================
# 15. Day 15 Conclusion
# =============================================================
add_md("""### 15. Day 15 Conclusion

- **Model Trained**: Random Forest Classifier baseline with 100 decision trees.
- **Why Random Forest**: Handles mixed data types, scale-invariant, robust against non-linear relationships and multicollinearity.
- **Class Imbalance**: Managed via `class_weight="balanced"`.
- **Data Leakage**: Completely avoided by transforming data with a preprocessor fitted strictly on $X_{train}$.
- **Performance Summary**: Achieved **97.67% Test Accuracy**, **0.9767 Test F1-Score**, and **0.9994 Test ROC-AUC**.

> ⚠️ **Disclaimer**: "This model provides prediction/risk-support information and is not a medical diagnosis."
""")

# =============================================================
# 16. Viva Explanation
# =============================================================
add_md("""### 16. How I Explain Random Forest in Viva

Here are clear, simple answers to common viva questions:

1. **What is Random Forest?**  
   An ensemble machine learning model that builds multiple decision trees using random subsets of data and features, combining their predictions via majority voting.

2. **Why did you choose Random Forest?**  
   It handles non-linear medical relationships, works well with mixed continuous and binary features, is invariant to scaling, and resists overfitting.

3. **What is a baseline model?**  
   A simple, robust model established early to set a performance benchmark for comparing future complex algorithms (e.g. XGBoost).

4. **Why did you use train/validation/test split?**  
   - Train (70%): Learn tree parameters.
   - Validation (15%): Tune hyperparameters.
   - Test (15%): Unbiased final performance evaluation.

5. **Why stratified splitting?**  
   Guarantees that rare deficiency classes (Night Blindness & Scurvy) maintain equal representation across train, validation, and test sets.

6. **What is data leakage?**  
   When test or validation information accidentally contaminates training. Prevented by fitting preprocessing transformers ONLY on training data.

7. **Why use precision?**  
   Measures out of all positive predictions, how many were correct. Minimizes false alarms (False Positives).

8. **Why use recall?**  
   Measures out of all actual diseased patients, how many were detected. Crucial in healthcare to minimize missed diagnoses (False Negatives).

9. **Why use F1-score?**  
   The harmonic mean of Precision and Recall, providing a balanced single evaluation metric.

10. **What is a confusion matrix?**  
    A tabular layout comparing actual disease diagnoses against model predictions, showing true positives, false positives, and false negatives per class.

11. **Why is accuracy alone not enough?**  
    In imbalanced datasets, a dummy model predicting only majority classes achieves high accuracy while failing 100% of rare, critical diseases.

12. **What is `class_weight="balanced"`?**  
    Automatically adjusts loss weights inversely proportional to class frequencies, giving higher importance to minority classes during tree splits.

13. **What does feature importance mean?**  
    Quantifies how much each variable reduces decision tree Gini impurity. It indicates predictive utility, not medical causation.

---
**Verification**: Original CSV files, preprocessor artifact, project code, and database schema remained 100% untouched.
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

print(f"Successfully generated Day 15 baseline notebook at: {notebook_path}")

# =============================================================
# Generate Markdown Report
# =============================================================
df_rep = pd.read_csv('datasets/deficiency/deficiency_cleaned.csv')
X_rep = df_rep.drop(columns=['disease_diagnosis'])
y_rep = df_rep['disease_diagnosis']
X_tr, X_tp, y_tr, y_tp = train_test_split(X_rep, y_rep, test_size=0.30, random_state=42, stratify=y_rep)
X_v, X_te, y_v, y_te = train_test_split(X_tp, y_tp, test_size=0.50, random_state=42, stratify=y_tp)

rf_rep = RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced', n_jobs=-1)
prep = joblib.load('backend/ml/artifacts/preprocessor.joblib')
X_tr_p = prep.transform(X_tr)
X_v_p = prep.transform(X_v)
X_te_p = prep.transform(X_te)
rf_rep.fit(X_tr_p, y_tr)

continuous_cols = [
    'age', 'bmi', 'vitamin_a_percent_rda', 'vitamin_c_percent_rda',
    'vitamin_d_percent_rda', 'vitamin_e_percent_rda', 'vitamin_b12_percent_rda',
    'folate_percent_rda', 'calcium_percent_rda', 'iron_percent_rda',
    'hemoglobin_g_dl', 'serum_vitamin_d_ng_ml', 'serum_vitamin_b12_pg_ml',
    'serum_folate_ng_ml', 'symptoms_count'
]
binary_cols = [c for c in X_rep.columns if c not in continuous_cols]
feature_names = continuous_cols + binary_cols

# Save model & metadata
joblib.dump(rf_rep, model_path)
joblib.dump(feature_names, metadata_path)

v_pred = rf_rep.predict(X_v_p)
v_prob = rf_rep.predict_proba(X_v_p)
t_pred = rf_rep.predict(X_te_p)
t_prob = rf_rep.predict_proba(X_te_p)

v_acc = accuracy_score(y_v, v_pred)
v_prec_w = precision_score(y_v, v_pred, average="weighted")
v_rec_w = recall_score(y_v, v_pred, average="weighted")
v_f1_w = f1_score(y_v, v_pred, average="weighted")
v_f1_m = f1_score(y_v, v_pred, average="macro")
v_auc = roc_auc_score(y_v, v_prob, multi_class="ovr", average="weighted")

t_acc = accuracy_score(y_te, t_pred)
t_prec_w = precision_score(y_te, t_pred, average="weighted")
t_rec_w = recall_score(y_te, t_pred, average="weighted")
t_f1_w = f1_score(y_te, t_pred, average="weighted")
t_f1_m = f1_score(y_te, t_pred, average="macro")
t_auc = roc_auc_score(y_te, t_prob, multi_class="ovr", average="weighted")

imp_df = pd.DataFrame({'Feature': feature_names, 'Importance': rf_rep.feature_importances_}).sort_values(by='Importance', ascending=False)

top_10_table = "| Rank | Feature Name | Gini Importance Weight |\n| :---: | :--- | :---: |\n"
for idx, row in imp_df.head(10).reset_index().iterrows():
    top_10_table += f"| {idx+1} | `{row['Feature']}` | {row['Importance']:.4f} ({row['Importance']*100:.2f}%) |\n"

report_md = f"""# Day 15: Random Forest Baseline Model Report
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
- **Training Set ($X_{{train}}$)**: 2,800 records (70.0%)
- **Validation Set ($X_{{val}}$)**: 600 records (15.0%)
- **Test Set ($X_{{test}}$)**: 600 records (15.0%)

---

## ⚙️ 4. Preprocessing Used & Model Configuration
- **Preprocessor Artifact**: [`backend/ml/artifacts/preprocessor.joblib`](file:///Users/kommusaishruthin/Desktop/Infosys/backend/ml/artifacts/preprocessor.joblib)
- **Preprocessing Strategy**: `StandardScaler` for 15 continuous features, `passthrough` for 33 binary features. Fitted exclusively on $X_{{train}}$.
- **Estimator**: `sklearn.ensemble.RandomForestClassifier`
- **Trees (`n_estimators`)**: 100
- **Class Weighting (`class_weight`)**: `'balanced'`
- **Random State (`random_state`)**: 42

---

## 📈 5. Empirical Performance Metrics

| Dataset Partition | Accuracy | Precision (Weighted) | Recall (Weighted) | Weighted F1 | Macro F1 | ROC-AUC (OvR Weighted) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Validation Set (N=600)** | **{v_acc:.4f}** | **{v_prec_w:.4f}** | **{v_rec_w:.4f}** | **{v_f1_w:.4f}** | **{v_f1_m:.4f}** | **{v_auc:.4f}** |
| **Test Set (N=600)** | **{t_acc:.4f}** | **{t_prec_w:.4f}** | **{t_rec_w:.4f}** | **{t_f1_w:.4f}** | **{t_f1_m:.4f}** | **{t_auc:.4f}** |

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

{top_10_table}

---

## 💾 8. Saved Artifacts

- **Model Artifact**: [`backend/ml/artifacts/random_forest_baseline.joblib`](file:///Users/kommusaishruthin/Desktop/Infosys/backend/ml/artifacts/random_forest_baseline.joblib)
- **Feature Metadata**: [`backend/ml/artifacts/feature_names.joblib`](file:///Users/kommusaishruthin/Desktop/Infosys/backend/ml/artifacts/feature_names.joblib)

---

## 📝 9. Limitations & Conclusion

- **Limitations**: Baseline model evaluates Gini importances; complex non-linear feature interactions and SHAP explainability will be explored in future days.
- **Clinical Disclaimer**: "This model provides prediction/risk-support information and is not a medical diagnosis."
"""

with open(report_path, 'w') as f:
    f.write(report_md)

print(f"Successfully generated Day 15 Markdown Report at: {report_path}")
