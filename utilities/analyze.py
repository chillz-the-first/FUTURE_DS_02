import pandas as pd

def get_baseline_churn_rate(df):
    churn_counts = df["Churn"].value_counts(normalize=True)
    return churn_counts["Yes"]

def get_churn_by(df, column):
    return (
        df.groupby(column, observed=False).agg(
            customers=("Churn_binary", "size"),
            churn_rate=("Churn_binary", "mean"),
        )
    )

def get_churn_by_tenure(df):
    df = df.copy()
    df["Tenure_Tier"] = pd.cut(
        df["tenure"],
        bins=[0, 12, 24, 48, float('inf')],
        labels=["0-1 yr", "1-2 yrs", "2-4 yrs", ">4 yrs"],
        include_lowest=True,
    )

    return get_churn_by(df, "Tenure_Tier")




