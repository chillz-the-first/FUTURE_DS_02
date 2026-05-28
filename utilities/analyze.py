def get_baseline_churn_rate(df):
    churn_counts = df["Churn"].value_counts(normalize=True)
    return churn_counts["Yes"]

