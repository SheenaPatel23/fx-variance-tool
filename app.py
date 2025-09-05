import streamlit as st
import pandas as pd
import numpy as np
import requests
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="FX Variance Tool", layout="wide")

st.title("💹 FX Variance Tool")
st.write("Compare budget FX rates vs daily/monthly ECB FX rates and analyse variances in operating costs.")

@st.cache_data
def load_budget_rates(file):
    return pd.read_csv(file)

@st.cache_data
def load_operating_costs(file):
    return pd.read_csv(file, parse_dates=["Date"])

@st.cache_data
def get_ecb_rates(start_date, end_date, symbols, base="EUR"):
    url = f"https://api.frankfurter.app/{start_date}..{end_date}?from={base}&to={','.join(symbols)}"
    r = requests.get(url)
    if r.status_code != 200:
        st.error("Error fetching ECB data")
        return pd.DataFrame()
    data = r.json()["rates"]
    df = pd.DataFrame(data).T.sort_index()
    df.index = pd.to_datetime(df.index)
    return df

st.sidebar.header("1. Upload Budget & Cost Data")
budget_file = st.sidebar.file_uploader("Upload budget FX rates (CSV)", type="csv")
cost_file = st.sidebar.file_uploader("Upload operating costs (CSV)", type="csv")

if budget_file and cost_file:
    budget_df = load_budget_rates(budget_file)
    cost_df = load_operating_costs(cost_file)

    st.subheader("📊 Budget FX Rates")
    st.dataframe(budget_df)

    st.subheader("📊 Operating Costs")
    st.dataframe(cost_df.head())

    report_ccy = budget_df["ReportCurrency"].iloc[0]
    currencies = budget_df["Currency"].unique().tolist()
    start_date, end_date = cost_df["Date"].min(), cost_df["Date"].max()

    st.sidebar.header("2. Fetch ECB FX Rates")
    if st.sidebar.button("Fetch ECB Data"):
        fx_df = get_ecb_rates(start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"), currencies, base=report_ccy)
        if not fx_df.empty:
            st.subheader("📈 ECB FX Rates")
            st.line_chart(fx_df)

            monthly_avg = fx_df.resample("M").mean()

            merged = cost_df.merge(budget_df, on="Currency", how="left")
            merged = merged.merge(monthly_avg, left_on=["Date"], right_index=True, how="left")
            for c in currencies:
                merged.loc[merged["Currency"] == c, "ActualRate"] = merged[c]

            merged["BudgetInReport"] = merged["BudgetLocal"] / merged["BudgetRateToReport"]
            merged["ActualInReport"] = merged["ActualLocal"] / merged["ActualRate"]
            merged["FXVariance"] = merged["BudgetInReport"] - (merged["ActualLocal"] / merged["BudgetRateToReport"])
            merged["CostVariance"] = merged["BudgetInReport"] - merged["ActualInReport"]
            merged["TotalVariance"] = merged["FXVariance"] + merged["CostVariance"]

            st.subheader("📑 Variance Table")
            st.dataframe(merged[["Date","CostCentre","Item","Currency","BudgetInReport","ActualInReport","FXVariance","CostVariance","TotalVariance"]])

            st.download_button("Download Variance Table (CSV)", merged.to_csv(index=False).encode("utf-8"), "variance_table.csv", "text/csv")

            st.subheader("📊 Variance by Cost Centre")
            fig1 = px.bar(merged, x="CostCentre", y="TotalVariance", color="CostCentre", title="Total Variance by Cost Centre")
            st.plotly_chart(fig1, use_container_width=True)

            st.subheader("📊 FX vs Cost Variance Waterfall (sample)")
            sample = merged.groupby("Currency")[["FXVariance","CostVariance"]].sum().reset_index().melt(id_vars="Currency")
            fig2 = px.bar(sample, x="Currency", y="value", color="variable", barmode="group", title="FX vs Cost Variance")
            st.plotly_chart(fig2, use_container_width=True)
