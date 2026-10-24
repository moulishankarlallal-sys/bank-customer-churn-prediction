import os

import numpy as np
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, roc_auc_score, ConfusionMatrixDisplay,
)

st.set_page_config(page_title="Bank Customer Churn Prediction", layout="wide")
st.title("Bank Customer Churn Prediction")

FEATURES = [
    "CreditScore", "Geography", "Gender", "Age", "Tenure",
    "Balance", "NumOfProducts", "HasCrCard", "IsActiveMember",
    "EstimatedSalary",
]
TARGET = "Exited"
NUMERIC = [
    "CreditScore", "Age", "Tenure", "Balance",
    "NumOfProducts", "HasCrCard", "IsActiveMember", "EstimatedSalary",
]
CATEGORICAL = ["Geography", "Gender"]

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_CSV = os.path.join(BASE_DIR, "European Bank.csv")


# ---------------------------------------------------------------
# Load data: uploaded file first, otherwise the CSV in the repo
# ---------------------------------------------------------------
uploaded = st.sidebar.file_uploader("Upload bank churn CSV", type="csv")

if uploaded is not None:
    df = pd.read_csv(uploaded)
elif os.path.exists(DEFAULT_CSV):
    df = pd.read_csv(DEFAULT_CSV)
else:
    st.info("Upload your churn CSV in the sidebar to begin "
            "(or add 'European Bank.csv' to the repo).")
    st.stop()

missing = [c for c in FEATURES + [TARGET] if c not in df.columns]
if missing:
    st.error(f"Missing columns in CSV: {missing}")
    st.stop()

df = df.dropna(subset=[TARGET]).copy()
df[TARGET] = pd.to_numeric(df[TARGET], errors="coerce")
df = df[df[TARGET].isin([0, 1])].copy()
df[TARGET] = df[TARGET].astype(int)

X = df[FEATURES].copy()
y = df[TARGET].copy()


# ---------------------------------------------------------------
# Train model (cached so it only runs once per dataset)
# ---------------------------------------------------------------
@st.cache_resource(show_spinner="Training Random Forest model...")
def train_model(X, y):
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )
    numeric_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
    ])
    categorical_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("onehot", OneHotEncoder(handle_unknown="ignore")),
    ])
    preprocessor = ColumnTransformer([
        ("numeric", numeric_pipeline, NUMERIC),
        ("categorical", categorical_pipeline, CATEGORICAL),
    ])
    model = Pipeline([
        ("preprocessor", preprocessor),
        ("classifier", RandomForestClassifier(
            n_estimators=300, min_samples_leaf=2,
            class_weight="balanced", random_state=42, n_jobs=-1,
        )),
    ])
    model.fit(X_train, y_train)
    return model, X_test, y_test


model, X_test, y_test = train_model(X, y)
y_pred = model.predict(X_test)
y_prob = model.predict_proba(X_test)[:, 1]


# ---------------------------------------------------------------
# Tabs
# ---------------------------------------------------------------
tab_data, tab_perf, tab_risk, tab_predict = st.tabs(
    ["Dataset", "Model performance", "Customer risk", "Predict a customer"]
)

with tab_data:
    c1, c2, c3 = st.columns(3)
    c1.metric("Customers", f"{len(df):,}")
    c2.metric("Churned", f"{int(y.sum()):,}")
    c3.metric("Churn rate", f"{y.mean() * 100:.2f}%")

    st.subheader("Sample records")
    st.dataframe(df.head(20), use_container_width=True)

    st.subheader("Churn distribution")
    fig, ax = plt.subplots(figsize=(5, 3.5))
    counts = y.value_counts().sort_index().rename(
        index={0: "Retained", 1: "Churned"}
    )
    counts.plot(kind="bar", ax=ax, rot=0)
    ax.set_xlabel("Customer status")
    ax.set_ylabel("Number of customers")
    st.pyplot(fig)

with tab_perf:
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Accuracy", f"{accuracy_score(y_test, y_pred):.3f}")
    m2.metric("Precision", f"{precision_score(y_test, y_pred, zero_division=0):.3f}")
    m3.metric("Recall", f"{recall_score(y_test, y_pred, zero_division=0):.3f}")
    m4.metric("F1-score", f"{f1_score(y_test, y_pred, zero_division=0):.3f}")
    m5.metric("ROC-AUC", f"{roc_auc_score(y_test, y_prob):.3f}")

    st.subheader("Confusion matrix")
    fig, ax = plt.subplots(figsize=(5, 4))
    ConfusionMatrixDisplay.from_predictions(y_test, y_pred, ax=ax)
    st.pyplot(fig)

with tab_risk:
    results = df.copy()
    results["Predicted_Churn_Probability"] = model.predict_proba(X)[:, 1]
    results["Predicted_Risk_Percent"] = (
        results["Predicted_Churn_Probability"] * 100
    ).round(2)
    results["Predicted_Risk_Category"] = pd.cut(
        results["Predicted_Churn_Probability"],
        bins=[-0.001, 0.30, 0.60, 1.0],
        labels=["Low", "Medium", "High"],
        include_lowest=True,
    )

    st.subheader("Risk category counts")
    risk_counts = results["Predicted_Risk_Category"].value_counts().reindex(
        ["Low", "Medium", "High"], fill_value=0
    )
    fig, ax = plt.subplots(figsize=(5, 3.5))
    risk_counts.plot(kind="bar", ax=ax, rot=0)
    ax.set_xlabel("Risk category")
    ax.set_ylabel("Number of customers")
    st.pyplot(fig)

    st.subheader("Top 10 highest-risk customers")
    show_cols = [c for c in [
        "CustomerId", "Geography", "Age", "Exited",
        "Predicted_Risk_Percent", "Predicted_Risk_Category",
    ] if c in results.columns]
    st.dataframe(
        results.sort_values("Predicted_Risk_Percent", ascending=False)[show_cols].head(10),
        use_container_width=True,
    )

    st.download_button(
        "Download all predictions (CSV)",
        data=results.to_csv(index=False).encode("utf-8"),
        file_name="bank_customer_churn_predictions.csv",
        mime="text/csv",
    )

with tab_predict:
    st.subheader("Enter customer details")
    col1, col2 = st.columns(2)
    with col1:
        credit = st.number_input("Credit score", 300, 900, 600)
        geography = st.selectbox("Geography", sorted(df["Geography"].dropna().unique()))
        gender = st.selectbox("Gender", sorted(df["Gender"].dropna().unique()))
        age = st.number_input("Age", 18, 100, 45)
        tenure = st.number_input("Tenure (years)", 0, 20, 5)
    with col2:
        balance = st.number_input("Balance", 0.0, 1_000_000.0, 100000.0, step=1000.0)
        products = st.number_input("Number of products", 1, 4, 2)
        has_card = st.selectbox("Has credit card", [1, 0],
                                format_func=lambda v: "Yes" if v == 1 else "No")
        active = st.selectbox("Is active member", [1, 0],
                              format_func=lambda v: "Yes" if v == 1 else "No")
        salary = st.number_input("Estimated salary", 0.0, 1_000_000.0, 80000.0, step=1000.0)

    if st.button("Predict churn risk"):
        new_customer = pd.DataFrame([{
            "CreditScore": credit, "Geography": geography, "Gender": gender,
            "Age": age, "Tenure": tenure, "Balance": balance,
            "NumOfProducts": products, "HasCrCard": has_card,
            "IsActiveMember": active, "EstimatedSalary": salary,
        }])
        prob = model.predict_proba(new_customer)[0, 1]
        if prob < 0.30:
            category = "Low"
        elif prob < 0.60:
            category = "Medium"
        else:
            category = "High"

        st.metric("Churn probability", f"{prob:.2%}")
        st.write(f"Risk category: **{category}**")
        if prob >= 0.5:
            st.warning("Churn likely")
        else:
            st.success("Retention likely")
