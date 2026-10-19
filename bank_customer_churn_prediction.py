# -*- coding: utf-8 -*-
"""
Bank Customer Churn Prediction (runs as a normal Python script, no Colab needed)
 
Put your CSV (for example Churn_Modelling.csv) in the same folder as this file.
Run:  python churn_prediction_fixed.py
Outputs are saved in the "artifacts" folder.
"""
 
import os
import glob
import json
import shutil
 
import joblib
import numpy as np
import pandas as pd
 
import matplotlib
matplotlib.use("Agg")  # saves charts to files, works on servers without a screen
import matplotlib.pyplot as plt
 
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    classification_report,
    confusion_matrix,
)
 
print("All libraries imported successfully!")
 
# ---------------------------------------------------------------
# 1. Load the dataset
# ---------------------------------------------------------------
file_path = "Churn_Modelling.csv"   # change this if your CSV has another name
 
if not os.path.exists(file_path):
    # fall back to the first CSV found in the script's folder
    script_dir = os.path.dirname(os.path.abspath(__file__))
    found = glob.glob(os.path.join(script_dir, "*.csv"))
    if not found:
        raise FileNotFoundError(
            "CSV file not found. Put your CSV in the same folder as this "
            "script and set file_path to its name."
        )
    file_path = found[0]
 
df = pd.read_csv(file_path)
 
print("Dataset loaded successfully from:", file_path)
print("Number of rows and columns:", df.shape)
print("\nColumn names:")
print(df.columns.tolist())
print("\nFirst five records:")
print(df.head())
print("\nMissing values in each column:")
print(df.isnull().sum())
print("\nDataset information:")
df.info()
 
os.makedirs("artifacts", exist_ok=True)
 
# ---------------------------------------------------------------
# 2. Churn distribution
# ---------------------------------------------------------------
print("\nChurn counts:")
print(df["Exited"].value_counts())
print("\nChurn percentages:")
print((df["Exited"].value_counts(normalize=True) * 100).round(2))
 
df["Exited"].value_counts().sort_index().plot(
    kind="bar",
    xlabel="Exited (0 = Retained, 1 = Churned)",
    ylabel="Number of Customers",
    title="Bank Customer Churn Distribution",
    rot=0,
)
plt.tight_layout()
plt.savefig("artifacts/churn_distribution.png", dpi=300)
plt.close()
 
# ---------------------------------------------------------------
# 3. Prepare features and target
# ---------------------------------------------------------------
features = [
    "CreditScore", "Geography", "Gender", "Age", "Tenure",
    "Balance", "NumOfProducts", "HasCrCard", "IsActiveMember",
    "EstimatedSalary",
]
target = "Exited"
 
required_columns = features + [target]
missing_columns = [c for c in required_columns if c not in df.columns]
if missing_columns:
    raise ValueError(f"Required columns are missing: {missing_columns}")
 
model_df = df[required_columns].copy()
model_df = model_df.dropna(subset=[target])
model_df[target] = pd.to_numeric(model_df[target], errors="coerce")
model_df = model_df.dropna(subset=[target])
 
if not model_df[target].isin([0, 1]).all():
    raise ValueError("Exited must contain only 0 and 1.")
 
model_df[target] = model_df[target].astype(int)
 
X = model_df[features]
y = model_df[target]
 
numeric_features = [
    "CreditScore", "Age", "Tenure", "Balance",
    "NumOfProducts", "HasCrCard", "IsActiveMember", "EstimatedSalary",
]
categorical_features = ["Geography", "Gender"]
 
print("\nFeatures and target prepared.")
print("Number of usable records:", len(model_df))
 
# ---------------------------------------------------------------
# 4. Train / test split
# ---------------------------------------------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.20, random_state=42, stratify=y
)
 
print("Training records:", len(X_train))
print("Testing records:", len(X_test))
 
# ---------------------------------------------------------------
# 5. Preprocessing
# ---------------------------------------------------------------
numeric_pipeline = Pipeline([
    ("imputer", SimpleImputer(strategy="median")),
    ("scaler", StandardScaler()),
])
 
categorical_pipeline = Pipeline([
    ("imputer", SimpleImputer(strategy="most_frequent")),
    ("encoder", OneHotEncoder(handle_unknown="ignore")),
])
 
preprocessor = ColumnTransformer([
    ("numeric", numeric_pipeline, numeric_features),
    ("categorical", categorical_pipeline, categorical_features),
])
 
# ---------------------------------------------------------------
# 6. Train three models
# ---------------------------------------------------------------
models = {
    "Logistic Regression": LogisticRegression(
        max_iter=1000, class_weight="balanced", random_state=42
    ),
    "Random Forest": RandomForestClassifier(
        n_estimators=200, max_depth=12, min_samples_leaf=3,
        class_weight="balanced", random_state=42, n_jobs=-1,
    ),
    "Gradient Boosting": GradientBoostingClassifier(
        n_estimators=150, learning_rate=0.05, max_depth=3, random_state=42
    ),
}
 
trained_models = {}
results = {}
 
for name, model in models.items():
    pipeline = Pipeline([("preprocessor", preprocessor), ("model", model)])
    print(f"Training {name}...")
    pipeline.fit(X_train, y_train)
 
    predictions = pipeline.predict(X_test)
    probabilities = pipeline.predict_proba(X_test)[:, 1]
 
    results[name] = {
        "Accuracy": accuracy_score(y_test, predictions),
        "Precision": precision_score(y_test, predictions, zero_division=0),
        "Recall": recall_score(y_test, predictions, zero_division=0),
        "F1 Score": f1_score(y_test, predictions, zero_division=0),
        "ROC-AUC": roc_auc_score(y_test, probabilities),
    }
    trained_models[name] = pipeline
 
print("\nAll three models trained successfully!")
 
results_df = pd.DataFrame(results).T
results_df.index.name = "Model"
results_df = results_df.sort_values(by="ROC-AUC", ascending=False)
print(results_df.round(4))
 
# ---------------------------------------------------------------
# 7. Best model evaluation
# ---------------------------------------------------------------
best_model_name = results_df.index[0]
best_model = trained_models[best_model_name]
 
best_predictions = best_model.predict(X_test)
print("\nBest model by ROC-AUC:", best_model_name)
print("\nClassification Report:")
print(classification_report(
    y_test, best_predictions,
    target_names=["Retained", "Churned"], zero_division=0,
))
 
cm = confusion_matrix(y_test, best_predictions)
print("Confusion Matrix:")
print(cm)
 
plt.figure(figsize=(6, 4))
plt.imshow(cm, interpolation="nearest")
plt.title(f"Confusion Matrix - {best_model_name}")
plt.xlabel("Predicted Class")
plt.ylabel("Actual Class")
plt.xticks([0, 1], ["Retained", "Churned"])
plt.yticks([0, 1], ["Retained", "Churned"])
for i in range(2):
    for j in range(2):
        plt.text(j, i, str(cm[i, j]), ha="center", va="center")
plt.tight_layout()
plt.savefig("artifacts/confusion_matrix.png", dpi=300)
plt.close()
 
# ---------------------------------------------------------------
# 8. Customer risk scores
# ---------------------------------------------------------------
risk_output = model_df[features].copy()
risk_output["Actual_Exited"] = y.values
risk_output["Churn_Probability"] = best_model.predict_proba(X)[:, 1]
risk_output["Risk_Percentage"] = (risk_output["Churn_Probability"] * 100).round(2)
risk_output["Risk_Category"] = pd.cut(
    risk_output["Churn_Probability"],
    bins=[-0.001, 0.30, 0.60, 1.00],
    labels=["Low Risk", "Medium Risk", "High Risk"],
)
 
print("\nRisk category counts:")
print(risk_output["Risk_Category"].value_counts())
print("\nTop 10 highest-risk customers:")
print(risk_output.sort_values("Churn_Probability", ascending=False).head(10))
 
# ---------------------------------------------------------------
# 9. Save model and results
# ---------------------------------------------------------------
joblib.dump(best_model, "artifacts/best_churn_model.joblib")
results_df.to_csv("artifacts/model_comparison.csv")
risk_output.to_csv("artifacts/customer_churn_risk_scores.csv", index=False)
 
metadata = {
    "best_model": best_model_name,
    "features": features,
    "target": target,
    "selection_metric": "ROC-AUC",
    "risk_thresholds": {
        "low": "below 30%",
        "medium": "30% to below 60%",
        "high": "60% or above",
    },
}
with open("artifacts/model_metadata.json", "w") as f:
    json.dump(metadata, f, indent=4)
 
print("\nModel and results saved successfully!")
 
# ---------------------------------------------------------------
# 10. Predict one new customer
# ---------------------------------------------------------------
new_customer = pd.DataFrame([{
    "CreditScore": 600,
    "Geography": "Germany",
    "Gender": "Male",
    "Age": 45,
    "Tenure": 5,
    "Balance": 100000,
    "NumOfProducts": 2,
    "HasCrCard": 1,
    "IsActiveMember": 0,
    "EstimatedSalary": 80000,
}])
 
probability = best_model.predict_proba(new_customer)[0, 1]
prediction = best_model.predict(new_customer)[0]
 
print(f"\nPredicted churn probability: {probability:.2%}")
print("Predicted outcome:", "Churn likely" if prediction == 1 else "Retention likely")
 
# ---------------------------------------------------------------
# 11. Charts
# ---------------------------------------------------------------
results_df[["Accuracy", "Precision", "Recall", "F1 Score", "ROC-AUC"]].plot(
    kind="bar", figsize=(12, 6)
)
plt.title("Bank Customer Churn - Model Performance Comparison")
plt.ylabel("Score")
plt.xlabel("Machine Learning Model")
plt.ylim(0, 1)
plt.xticks(rotation=15)
plt.legend(loc="lower right")
plt.tight_layout()
plt.savefig("artifacts/model_performance.png", dpi=300)
plt.close()
 
risk_counts = risk_output["Risk_Category"].value_counts().reindex(
    ["Low Risk", "Medium Risk", "High Risk"], fill_value=0
)
risk_counts.plot(kind="bar", figsize=(8, 5), rot=0)
plt.title("Customer Churn Risk Distribution")
plt.xlabel("Risk Category")
plt.ylabel("Number of Customers")
plt.tight_layout()
plt.savefig("artifacts/risk_distribution.png", dpi=300)
plt.close()
 
fitted_preprocessor = best_model.named_steps["preprocessor"]
fitted_model = best_model.named_steps["model"]
 
if hasattr(fitted_model, "feature_importances_"):
    importance_df = pd.DataFrame({
        "Feature": fitted_preprocessor.get_feature_names_out(),
        "Importance": fitted_model.feature_importances_,
    }).sort_values("Importance", ascending=False)
 
    print("\nTop 15 features:")
    print(importance_df.head(15))
 
    importance_df.head(15).sort_values("Importance").plot(
        x="Feature", y="Importance", kind="barh", figsize=(10, 7), legend=False
    )
    plt.title("Top Features Associated with Churn Predictions")
    plt.xlabel("Feature Importance")
    plt.tight_layout()
    plt.savefig("artifacts/feature_importance.png", dpi=300)
    plt.close()
else:
    print(
        "\nThe selected model does not expose tree-based feature importance. "
        "Use permutation importance for this model."
    )
 
# ---------------------------------------------------------------
# 12. Zip everything
# ---------------------------------------------------------------
shutil.make_archive("bank_churn_final_results", "zip", "artifacts")
print("\nDone! Results saved in the 'artifacts' folder and bank_churn_final_results.zip")
 
