def get_baseline_churn_rate(df):
    churn_counts = df["Churn"].value_counts(normalize=True)
    return churn_counts["Yes"]

def get_churn_by_contract(df):
    # contract_churn = df.groupby("Contract")["Churn"].value_counts(normalize=True).reset_index()
    # contract_churn.columns = ["Contract", "Churn", "Churn_rate"]
    # contract_churn["Churn_rate"] = contract_churn["Churn_rate"].map('{:.1%}'.format)

    df["Churn_binary"] = (df["Churn"] == "Yes").astype(int)
    rate = df.groupby("Contract").agg(
        customers=("Churn_binary", "size"),
        churn_rate=("Churn_binary", "mean"),
    )

    return rate
