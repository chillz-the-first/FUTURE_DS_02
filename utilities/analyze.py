import pandas as pd

def get_baseline_churn_rate(df):
    churn_counts = df["Churn"].value_counts(normalize=True)
    return churn_counts["Yes"]

def get_churn_by(df, column):
    print(f"\nChurn rate for {column}")

    return (
        df.groupby(column, observed=False).agg(
            customers=("Churn_binary", "size"),
            churn_rate=("Churn_binary", "mean"),
        )
    )

def get_lost_revenue(df, column):
    df = df.copy()
    df["Lost_Revenue"] = df["MonthlyCharges"] * df["Churn_binary"]
    print(f"\nLost Revenue for {column}")

    return (
        df.groupby(column, observed=False).agg(
            customers=("Churn_binary", "size"),
            churn_rate=("Churn_binary", "mean"),
            total_revenue=("MonthlyCharges", "sum"),
            lost_revenue=("Lost_Revenue", "sum"),
        )
    )




