"""
Store Cost Prediction Models
============================

Predicts expected monthly food and labor costs for each store from revenue and
operating company, then flags stores whose actual costs break from the
prediction.

This is a portfolio version of a model I run in production. The original reads
from Azure SQL; this version generates synthetic data with the same shape so it
runs anywhere without credentials or confidential data.

Pipeline
    1. Generate (or load) long-format ledger data: one row per store, account, month
    2. Join to a chart of accounts and a store master table
    3. Aggregate and pivot to one row per store-month with a column per category
    4. Train Linear, Ridge (tuned), and Random Forest models
    5. Compare models and flag cost outliers

Usage
    python cost_prediction.py
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

RANDOM_STATE = 42


# ---------------------------------------------------------------------------
# 1. Synthetic data
# ---------------------------------------------------------------------------

def make_reference_tables(n_stores: int = 120):
    """Build a chart of accounts and a store master table."""
    rng = np.random.default_rng(RANDOM_STATE)

    chart_of_accounts = pd.DataFrame({
        "AccountNumber": [400, 410, 420, 424, 500, 507, 508],
        "Description": ["Sales", "Meat", "Produce", "Tortillas",
                        "Staff Labor", "Sick Pay", "Vacation Pay"],
        "Category": ["Revenue", "Food Cost", "Food Cost", "Food Cost",
                     "Store Level Labor", "Store Level Labor", "Store Level Labor"],
    })

    companies = ["Company A", "Company B", "Company C", "Company D"]
    stores = pd.DataFrame({
        "StoreNumber": np.arange(1001, 1001 + n_stores),
        "Company": rng.choice(companies, size=n_stores),
        "Status": rng.choice(["Open", "Closed"], size=n_stores, p=[0.95, 0.05]),
    })
    return chart_of_accounts, stores


def make_ledger(stores: pd.DataFrame, months: int = 24) -> pd.DataFrame:
    """Generate long-format monthly ledger amounts by store and account."""
    rng = np.random.default_rng(RANDOM_STATE)
    dates = pd.date_range("2023-01-31", periods=months, freq="ME")

    # Each company runs at a slightly different cost structure
    food_rate = {"Company A": 0.28, "Company B": 0.30, "Company C": 0.26, "Company D": 0.29}
    labor_rate = {"Company A": 0.27, "Company B": 0.29, "Company C": 0.31, "Company D": 0.26}
    food_split = {410: 0.60, 420: 0.25, 424: 0.15}
    labor_split = {500: 0.94, 507: 0.03, 508: 0.03}

    rows = []
    for _, store in stores.iterrows():
        base_sales = rng.uniform(100_000, 250_000)
        for i, date in enumerate(dates):
            seasonality = 1 + 0.06 * np.sin(2 * np.pi * date.month / 12)
            sales = base_sales * seasonality * (1 + 0.002 * i) * rng.normal(1, 0.05)
            # Labor has a fixed component, so it doesn't scale perfectly with sales
            food = sales * food_rate[store.Company] * rng.normal(1, 0.04)
            labor = (12_000 + sales * labor_rate[store.Company] * 0.85) * rng.normal(1, 0.06)

            # Revenue is stored as a credit (negative), as in a real GL
            rows.append((store.StoreNumber, 400, date, -round(sales, 2)))
            for acct, share in food_split.items():
                rows.append((store.StoreNumber, acct, date, round(food * share, 2)))
            for acct, share in labor_split.items():
                rows.append((store.StoreNumber, acct, date, round(labor * share, 2)))

    return pd.DataFrame(rows, columns=["StoreID", "AccountID", "Date", "Amount"])


# ---------------------------------------------------------------------------
# 2-3. Transform
# ---------------------------------------------------------------------------

def build_store_month_table(ledger, chart_of_accounts, stores) -> pd.DataFrame:
    """Join reference tables, drop closed stores, and pivot to store-month rows."""
    df = (
        ledger
        .merge(chart_of_accounts[["AccountNumber", "Category"]],
               left_on="AccountID", right_on="AccountNumber", how="left")
        .merge(stores, left_on="StoreID", right_on="StoreNumber", how="left")
    )
    df = df[df["Status"] != "Closed"]

    pivoted = (
        df.pivot_table(index=["Date", "StoreID", "Company"], columns="Category",
                       values="Amount", aggfunc="sum")
        .reset_index()
        .fillna(0)
    )
    pivoted.columns.name = None
    pivoted["Revenue"] = -pivoted["Revenue"]  # flip GL credit to a positive number
    return pivoted[pivoted["Revenue"] > 0]


# ---------------------------------------------------------------------------
# 4. Models
# ---------------------------------------------------------------------------

def get_features(data: pd.DataFrame) -> pd.DataFrame:
    dummies = pd.get_dummies(data["Company"], prefix="Company", drop_first=True, dtype=int)
    return pd.concat([data[["Revenue"]], dummies], axis=1)


def train_and_compare(data: pd.DataFrame, target: str) -> pd.DataFrame:
    """Train three models for one target and return their validation scores."""
    X, y = get_features(data), data[target]
    X_train, X_valid, y_train, y_valid = train_test_split(
        X, y, test_size=0.2, random_state=RANDOM_STATE)

    ridge_search = GridSearchCV(
        make_pipeline(StandardScaler(), Ridge()),
        {"ridge__alpha": [0.01, 0.1, 1, 10, 100]}, cv=5)

    models = {
        "Linear Regression": make_pipeline(StandardScaler(), LinearRegression()),
        "Ridge (tuned)": ridge_search,
        "Random Forest": RandomForestRegressor(n_estimators=200, random_state=RANDOM_STATE),
    }

    results = []
    for name, model in models.items():
        model.fit(X_train, y_train)
        pred = model.predict(X_valid)
        results.append({
            "Target": target,
            "Model": name,
            "RMSE": np.sqrt(mean_squared_error(y_valid, pred)),
            "R2": r2_score(y_valid, pred),
        })
    return pd.DataFrame(results), models


# ---------------------------------------------------------------------------
# 5. Flag outliers
# ---------------------------------------------------------------------------

def flag_outliers(data, model, target: str, threshold: float = 0.08) -> pd.DataFrame:
    """Flag store-months where actual cost differs from predicted by more than threshold."""
    out = data[["Date", "StoreID", "Company", "Revenue", target]].copy()
    out[f"Predicted {target}"] = model.predict(get_features(data))
    out["Difference %"] = (out[target] - out[f"Predicted {target}"]) / out[f"Predicted {target}"]
    return out[out["Difference %"].abs() > threshold].sort_values("Difference %", ascending=False)


def main():
    chart_of_accounts, stores = make_reference_tables()
    ledger = make_ledger(stores)
    data = build_store_month_table(ledger, chart_of_accounts, stores)
    print(f"Store-month rows: {len(data):,}  |  Stores: {data['StoreID'].nunique()}\n")

    all_results, fitted = [], {}
    for target in ["Food Cost", "Store Level Labor"]:
        results, models = train_and_compare(data, target)
        all_results.append(results)
        fitted[target] = models

    print("Model comparison (validation set)")
    print(pd.concat(all_results).round({"RMSE": 0, "R2": 3}).to_string(index=False))

    outliers = flag_outliers(data, fitted["Store Level Labor"]["Random Forest"], "Store Level Labor")
    print(f"\nStore-months with labor cost more than 8% off prediction: {len(outliers)}")
    outliers["Date"] = outliers["Date"].dt.strftime("%Y-%m")
    print(outliers.head(10).round(2).to_string(index=False))


if __name__ == "__main__":
    main()
