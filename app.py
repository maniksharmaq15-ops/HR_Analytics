from pathlib import Path
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="HR Analytics Dashboard", layout="wide")
st.title("HR Analytics Dashboard")

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"


def load_sample_data() -> pd.DataFrame:
    rng = np.random.default_rng(42)
    departments = ["Engineering", "Sales", "HR", "Operations", "Finance"]
    n = 150
    return pd.DataFrame(
        {
            "EmployeeID": [f"EMP{1000 + i}" for i in range(n)],
            "Department": rng.choice(departments, size=n, p=[0.32, 0.25, 0.10, 0.20, 0.13]),
            "MonthlyIncome": rng.integers(32000, 145000, size=n),
            "JobSatisfaction": rng.integers(1, 5, size=n),
            "Attrition": rng.choice(["Yes", "No"], size=n, p=[0.16, 0.84]),
        }
    )


@st.cache_data
def load_hr_data() -> pd.DataFrame:
    csv_files = list(DATA_DIR.glob("*.csv")) + list(BASE_DIR.glob("*.csv"))
    if csv_files:
        return pd.read_csv(csv_files[0])
    return load_sample_data()


df = load_hr_data()

# Sidebar filters
st.sidebar.header("Filters")
if "Department" in df.columns:
    dept_options = sorted(df["Department"].dropna().unique().tolist())
    selected_depts = st.sidebar.multiselect("Department", dept_options, default=dept_options)
    if selected_depts:
        df = df[df["Department"].isin(selected_depts)]

# KPI row
col1, col2, col3 = st.columns(3)
col1.metric("Total Employees", f"{len(df):,}")

if "MonthlyIncome" in df.columns and len(df) > 0:
    col2.metric("Average Monthly Income", f"{df['MonthlyIncome'].mean():,.0f}")
else:
    col2.metric("Average Monthly Income", "N/A")

if "Attrition" in df.columns and len(df) > 0:
    attrition_rate = (df["Attrition"].astype(str).str.lower() == "yes").mean() * 100
    col3.metric("Attrition Rate", f"{attrition_rate:.1f}%")
else:
    col3.metric("Attrition Rate", "N/A")

# Charts
chart_col1, chart_col2 = st.columns(2)
if "Department" in df.columns:
    dept_counts = df["Department"].value_counts().reset_index()
    dept_counts.columns = ["Department", "Headcount"]
    fig_dept = px.bar(dept_counts, x="Department", y="Headcount", title="Headcount by Department")
    chart_col1.plotly_chart(fig_dept, use_container_width=True)

if "Department" in df.columns and "MonthlyIncome" in df.columns:
    fig_income = px.box(df, x="Department", y="MonthlyIncome", title="Income Distribution by Department")
    chart_col2.plotly_chart(fig_income, use_container_width=True)

st.subheader("Employee Records")
st.dataframe(df, use_container_width=True)
