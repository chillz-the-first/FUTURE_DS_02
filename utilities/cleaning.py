"""
Utilities for inspecting and cleaning the Superstore dataset.

This module provides reusable functions that handle the standard data-quality
workflow: report on a DataFrame's state, check categorical consistency, find
outliers, standardise text columns, and run the full cleaning pipeline.
"""
import pandas as pd

CATEGORICAL_TEXT_COLS = ["gender", "Partner", "Dependents", "PhoneService", "MultipleLines",
                         "InternetService", "OnlineSecurity", "OnlineBackup", "DeviceProtection",
                         "TechSupport", "StreamingTV", "StreamingMovies", "Contract",
                         "PaperlessBilling", "PaymentMethod"]

def report(df):
    """
    Print a quick diagnostic summary of a DataFrame.

    Shows shape, duplicate count, missing-value counts per column,
    the first/last 5 rows, and the column dtypes via df.info().
    Useful as a "before and after" snapshot when cleaning.
    """
    print(f"Total rows: {df.shape[0]}, Total columns: {df.shape[1]}")

    total_dupes = df.duplicated().sum()
    print(f"\nDuplicate rows: {total_dupes}")

    null_values = df.isnull().sum()
    null_values = null_values[null_values != 0]
    if len(null_values) > 0:
        print("\nMissing values:")
        for col, val in null_values.items():
                print(f"{col}: {val} missing values")
    else:
        print("\nNo missing values")

    print("\nThe first and last 5 rows of the dataset:")
    print(df.head(5))
    print(df.tail(5))

    print()
    df.info()


def check_categories(df):
    """
    Print value_counts() for each categorical column we care about.

    Useful for spotting casing/whitespace inconsistencies — e.g. 'West'
    and ' west ' showing up as separate categories. Skips numeric columns
    silently.
    """
    cols = [col for col in df.columns if col in CATEGORICAL_TEXT_COLS]

    for col in cols:
        if pd.api.types.is_numeric_dtype(df[col]):
          continue
        print(f"Categories in {col}")
        print(df[col].value_counts())
        print()








