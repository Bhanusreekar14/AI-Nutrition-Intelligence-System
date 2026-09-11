#!/usr/bin/env python3
"""
Validation script for cleaned nutritional deficiency dataset.
AI Nutrition Intelligence System (Week 3 — Day 13)

Validates datasets/deficiency/deficiency_cleaned.csv against quality standards.
"""

import os
import sys
import hashlib
import pandas as pd


def validate():
    print("=" * 70)
    print("DAY 13 CLEANED DATASET VALIDATION")
    print("=" * 70)

    orig_path = 'datasets/deficiency/deficiency_preprocessed.csv'
    clean_path = 'datasets/deficiency/deficiency_cleaned.csv'

    # Check 1: Original file hash integrity
    expected_orig_md5 = '719b63c8e630c00cbe02553fdb6d7e15'
    with open(orig_path, 'rb') as f:
        actual_orig_md5 = hashlib.md5(f.read()).hexdigest()

    orig_unmodified = (actual_orig_md5 == expected_orig_md5)
    print(f"\n1. Original CSV Read-Only Integrity:")
    print(f"   Expected MD5 : {expected_orig_md5}")
    print(f"   Actual MD5   : {actual_orig_md5}")
    print(f"   Status       : {'PASS' if orig_unmodified else 'FAIL'}")

    # Check 2: Cleaned file existence
    clean_exists = os.path.exists(clean_path)
    print(f"\n2. Cleaned File Existence:")
    print(f"   Path   : {clean_path}")
    print(f"   Status : {'PASS' if clean_exists else 'FAIL'}")

    if not clean_exists:
        print("ERROR: Cleaned file does not exist!")
        sys.exit(1)

    # Check 3: Load cleaned file and verify shape
    df_clean = pd.read_csv(clean_path)
    rows, cols = df_clean.shape
    print(f"\n3. Cleaned Dataset Dimensions:")
    print(f"   Shape  : {rows} rows x {cols} columns")
    print(f"   Status : {'PASS' if (rows == 4000 and cols == 49) else 'FAIL'}")

    # Check 4: Missing values
    total_nulls = df_clean.isnull().sum().sum()
    print(f"\n4. Missing Values Check:")
    print(f"   Nulls  : {total_nulls}")
    print(f"   Status : {'PASS' if total_nulls == 0 else 'FAIL'}")

    # Check 5: Duplicate rows
    dup_rows = df_clean.duplicated().sum()
    print(f"\n5. Duplicate Rows Check:")
    print(f"   Duplicates : {dup_rows}")
    print(f"   Status     : {'PASS' if dup_rows == 0 else 'FAIL'}")

    # Check 6: Target column name & classes
    has_target = 'disease_diagnosis' in df_clean.columns
    target_classes = sorted(list(df_clean['disease_diagnosis'].unique())) if has_target else []
    print(f"\n6. Target Column & Label Check:")
    print(f"   Target Present : {has_target} ('disease_diagnosis')")
    print(f"   Target Classes : {target_classes}")
    print(f"   Status         : {'PASS' if (has_target and target_classes == [0, 1, 2, 3, 4]) else 'FAIL'}")

    all_passed = orig_unmodified and clean_exists and (rows == 4000 and cols == 49) and (total_nulls == 0) and (dup_rows == 0) and (target_classes == [0, 1, 2, 3, 4])

    print("\n" + "=" * 70)
    print(f"OVERALL VALIDATION RESULT: {'ALL CHECKS PASSED ✅' if all_passed else 'VALIDATION FAILED ❌'}")
    print("=" * 70)

    if not all_passed:
        sys.exit(1)


if __name__ == '__main__':
    validate()
