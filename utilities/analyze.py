"""
Analysis and plotting utilities for the Telco churn project.

Convention: functions starting with `get_` return a DataFrame for inspection
or downstream use. Functions starting with `plot_` draw onto a Matplotlib axes
passed in by the caller — they never create their own figure.
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme(style="whitegrid")

def get_baseline_churn_rate(df):
    """Return the overall churn rate (proportion of customers who churned)."""
    churn_counts = df["Churn"].value_counts(normalize=True)
    return churn_counts["Yes"]

def get_churn_by(df, column):
    """
    Customer count and churn rate for each value of `column`.

    Relies on a pre-computed `Churn_binary` column (1 = churned, 0 = retained).
    The mean of a 0/1 column inside a group is, by definition, the churn rate
    for that group.
    """
    return (
        df.groupby(column, observed=False).agg(
            customers=("Churn_binary", "size"),
            churn_rate=("Churn_binary", "mean"),
        )
    )

def get_lost_revenue(df, column):
    """
    For each value of `column`, return customer count, churn rate, total monthly
    revenue, and monthly revenue lost to churn.

    Lost revenue = MonthlyCharges * Churn_binary (zero for retained customers,
    full monthly charge for churners). Summed over the group, this is the
    monthly recurring revenue the company is losing from that segment.
    """
    df = df.copy()
    df["Lost_Revenue"] = df["MonthlyCharges"] * df["Churn_binary"]

    return (
        df.groupby(column, observed=False).agg(
            customers=("Churn_binary", "size"),
            churn_rate=("Churn_binary", "mean"),
            total_revenue=("MonthlyCharges", "sum"),
            lost_revenue=("Lost_Revenue", "sum"),
        )
    )

def get_retention_curve(df):
    """
    Retention rate at each month of tenure (0 to 72).

    For each tenure value, retention = 1 - churn_rate. Plotting the result
    gives the familiar steep-then-flattening retention curve, which makes
    the front-loaded nature of churn visible at a glance.
    """
    tenure_grouped = df.groupby("tenure").agg(
        total_customers=("Churn_binary", "size"),
        churn_rate=("Churn_binary", "mean"),
    )

    tenure_grouped["retention_rate"] = 1 - tenure_grouped["churn_rate"]
    return tenure_grouped

_BAR_PALETTE = "Set2"
_LINE_COLOR = "#1f77b4"
_LABEL_OFFSET = 0.01

def plot_churn_rate_by(churn_df, ax, column, baseline=None):
    """
    Bar chart of churn rate per segment.

    `column` is the segmentation column name (Contract, InternetService,
    PaymentMethod, etc.).

    If `baseline` is given, draw a dashed reference line at that y-value
    (useful for showing the overall churn rate above which a segment is
    worse than average).
    """
    data = churn_df.drop(columns=["customers"]).reset_index()

    sns.barplot(
        data=data,
        x=column,
        y="churn_rate",
        hue=column,
        palette=_BAR_PALETTE,
        legend=False,
        ax=ax,
    )

    if baseline is not None:
        ax.axhline(y=baseline, color="red", linestyle="--",
                   linewidth=1.5, label=f"Baseline ({baseline:.1%})")
        ax.legend(loc="upper right")

    ax.set_title(f"Churn rate by {column.lower()}")
    ax.set(xlabel=column, ylabel="Churn rate (%)")
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f'{y:.0%}'))

    for index, row in data.iterrows():
        ax.text(index, row["churn_rate"] + _LABEL_OFFSET, f"{row['churn_rate']:.1%}"
                 , ha="center", fontsize=10)

def plot_contract_revenue_risk(contract, ax):
    """
    Grouped bar chart comparing total monthly revenue vs lost revenue per
    contract type. Designed for the output of `get_lost_revenue(df, "Contract")`.
    """
    data = contract.drop(columns=["customers", "churn_rate"]).reset_index()
    melted = data.melt(id_vars="Contract", var_name="Metric", value_name="Revenue")

    melted["Metric"] = melted["Metric"].replace({
        "total_revenue": "Total revenue",
        "lost_revenue": "Lost revenue",
    })

    sns.barplot(
        data=melted,
        x="Contract",
        y="Revenue",
        hue="Metric",
        palette=_BAR_PALETTE,
        legend=True,
        ax=ax,
    )

    ax.set_title("Revenue at risk by contract")
    ax.set(xlabel="Contract", ylabel="Revenue")

    for container in ax.containers:
        ax.bar_label(container, fmt="${:,.0f}", fontsize=10, padding=3)

def plot_retention_curve(retention, ax):
    """Line chart of retention rate against tenure (months)."""
    data = retention.drop(columns=["total_customers", "churn_rate"]).reset_index()

    sns.lineplot(
        data=data,
        x="tenure",
        y="retention_rate",
        color=_LINE_COLOR,
        marker="o",
        legend=False,
        linewidth=2,
        ax=ax,
    )

    ax.set_title("Tenure retention curve")
    ax.set(xlabel="Tenure", ylabel="Retention rate")
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f'{y:.0%}'))


def get_dashboard(contract, contract_risk, retention, internet, baseline, save_path=None):
    """
    Render the 2x2 dashboard summarising the four headline findings:
      - Churn rate by contract (with overall baseline line)
      - Revenue at risk by contract (grouped: total vs lost)
      - Tenure retention curve
      - Churn rate by internet service

    `baseline` is the overall churn rate, drawn as a dashed reference line
    on the contract panel. `save_path` writes the dashboard to disk if given.
    """
    fig,axes = plt.subplots(nrows=2, ncols=2, figsize=(16, 12))

    plot_churn_rate_by(contract, axes[0, 0], column="Contract", baseline=baseline)
    plot_contract_revenue_risk(contract_risk, axes[0, 1])
    plot_retention_curve(retention, axes[1, 0])
    plot_churn_rate_by(internet, axes[1, 1], column="InternetService")

    plt.tight_layout()
    if save_path is not None:
        plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.show()

