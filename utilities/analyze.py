import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme(style="whitegrid")

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

def get_retention_curve(df):
    tenure_grouped = df.groupby("tenure").agg(
        total_customers=("Churn_binary", "size"),
        churn_rate=("Churn_binary", "mean"),
    )

    tenure_grouped["retention_rate"] = 1 - tenure_grouped["churn_rate"]

    return tenure_grouped

def plot_churn_rate_by(churn_df, ax):
    data = churn_df.drop(columns=["customers"]).reset_index()

    if "Contract" in data.columns:
        x_val = "Contract"
        hue_val = "Contract"
        title = "Churn rate by contract"
        x_label = "Contract"
    else:
        x_val = "InternetService"
        hue_val = "InternetService"
        title = "Churn rate by internet service"
        x_label = "Internet Service"

    sns.barplot(
        data=data,
        x=x_val,
        y="churn_rate",
        hue=hue_val,
        palette="Set2",
        legend=False,
        ax=ax,
    )

    if x_val == "Contract":
        ax.axhline(y=0.265, color='red', linestyle='--', linewidth=1.5, label='Baseline (26.5%)')
        ax.legend(loc='upper right')

    ax.set_title(title)
    ax.set(xlabel=x_label, ylabel="Churn rate (%)")

    for index, row in data.iterrows():
        ax.text(index, row["churn_rate"] + 0.0001, f"{row['churn_rate']:.1%}"
                 , ha="center", fontsize=10)

def plot_contract_revenue_risk(contract, ax):
    data = contract.drop(columns=["customers", "churn_rate"]).reset_index()
    melted = data.melt(id_vars="Contract", var_name="Metric", value_name="Revenue")

    sns.barplot(
        data=melted,
        x="Contract",
        y="Revenue",
        hue="Metric",
        palette="Set2",
        legend=True,
        ax=ax,
    )

    ax.set_title("Revenue at risk by contract")
    ax.set(xlabel="Contract", ylabel="Revenue")

    for container in ax.containers:
        ax.bar_label(container, fmt="$%.0fK", fontsize=10, padding=3)

def plot_retention_curve(retention, ax):
    data = retention.drop(columns=["total_customers", "churn_rate"]).reset_index()

    sns.lineplot(
        data=data,
        x="tenure",
        y="retention_rate",
        color="#1f77b4",
        marker="o",
        legend=False,
        linewidth=2,
        ax=ax,
    )

    ax.set_title("Tenure retention curve")
    ax.set(xlabel="Tenure", ylabel="Retention rate")
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f'{y:.0%}'))

def get_dashboard(contract, retention, internet):
    fig,axes = plt.subplots(nrows=2, ncols=2, figsize=(16, 12))

    plot_churn_rate_by(contract, axes[0, 0])
    plot_contract_revenue_risk(contract, axes[0, 1])
    plot_retention_curve(retention, axes[1, 0])
    plot_churn_rate_by(internet, axes[1, 1])

    plt.tight_layout()
    plt.show()

