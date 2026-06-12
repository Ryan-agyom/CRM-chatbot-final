from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import (
    AdaBoostRegressor,
    ExtraTreesRegressor,
    GradientBoostingRegressor,
    RandomForestRegressor,
)
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, r2_score, root_mean_squared_error
from sklearn.model_selection import KFold, train_test_split
from sklearn.multioutput import MultiOutputRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.tree import DecisionTreeRegressor


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_ROOT / "data" / "crm_campaigns.csv"

FEATURES = ["campaign_type", "target_industry", "budget", "clicks"]
TARGETS = ["conversions", "conversion_rate"]


def build_preprocessor() -> ColumnTransformer:
    categorical_features = ["campaign_type", "target_industry"]
    numeric_features = ["budget", "clicks"]

    categorical_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore")),
        ]
    )

    numeric_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
        ]
    )

    return ColumnTransformer(
        transformers=[
            ("cat", categorical_pipeline, categorical_features),
            ("num", numeric_pipeline, numeric_features),
        ]
    )


def build_model_pipelines() -> dict[str, Pipeline]:
    preprocessor = build_preprocessor()

    models = {
        "linear_regression": LinearRegression(),
        "decision_tree": DecisionTreeRegressor(
            max_depth=6,
            min_samples_leaf=3,
            random_state=42,
        ),
        "random_forest": RandomForestRegressor(
            n_estimators=250,
            max_depth=10,
            min_samples_leaf=3,
            random_state=42,
            n_jobs=-1,
        ),
        "extra_trees": ExtraTreesRegressor(
            n_estimators=250,
            max_depth=10,
            min_samples_leaf=3,
            random_state=42,
            n_jobs=-1,
        ),
        "gradient_boosting": MultiOutputRegressor(
            GradientBoostingRegressor(
                n_estimators=200,
                learning_rate=0.05,
                max_depth=3,
                random_state=42,
            )
        ),
        "ada_boost": MultiOutputRegressor(
            AdaBoostRegressor(
                n_estimators=150,
                learning_rate=0.05,
                random_state=42,
            )
        ),
    }

    pipelines: dict[str, Pipeline] = {}
    for name, model in models.items():
        pipelines[name] = Pipeline(
            steps=[
                ("preprocessor", preprocessor),
                ("regressor", model),
            ]
        )
    return pipelines


def prepare_dataset() -> tuple[pd.DataFrame, pd.DataFrame]:
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Dataset not found: {DATA_PATH}")

    df = pd.read_csv(DATA_PATH)
    df = df[df[TARGETS].notna().all(axis=1)].copy()

    if df.empty:
        raise ValueError("No trainable rows found for campaign conversion prediction.")

    X = df[FEATURES].copy()
    y = df[TARGETS].copy()
    return X, y


def evaluate_with_cross_validation(X: pd.DataFrame, y: pd.DataFrame) -> pd.DataFrame:
    pipelines = build_model_pipelines()
    cv = KFold(n_splits=5, shuffle=True, random_state=42)

    rows: list[dict] = []

    for name, pipeline in pipelines.items():
        conversions_mae_scores = []
        conversions_rmse_scores = []
        conversions_r2_scores = []

        rate_mae_scores = []
        rate_rmse_scores = []
        rate_r2_scores = []

        for train_idx, test_idx in cv.split(X):
            X_train = X.iloc[train_idx]
            X_test = X.iloc[test_idx]
            y_train = y.iloc[train_idx]
            y_test = y.iloc[test_idx]

            pipeline.fit(X_train, y_train)
            preds = pipeline.predict(X_test)
            pred_df = pd.DataFrame(preds, columns=TARGETS, index=y_test.index)

            conversions_mae_scores.append(
                mean_absolute_error(y_test["conversions"], pred_df["conversions"])
            )
            conversions_rmse_scores.append(
                root_mean_squared_error(
                    y_test["conversions"],
                    pred_df["conversions"],
                )
            )
            conversions_r2_scores.append(
                r2_score(y_test["conversions"], pred_df["conversions"])
            )

            rate_mae_scores.append(
                mean_absolute_error(y_test["conversion_rate"], pred_df["conversion_rate"])
            )
            rate_rmse_scores.append(
                root_mean_squared_error(
                    y_test["conversion_rate"],
                    pred_df["conversion_rate"],
                )
            )
            rate_r2_scores.append(
                r2_score(y_test["conversion_rate"], pred_df["conversion_rate"])
            )

        rows.append(
            {
                "model": name,
                "conv_mae_mean": np.mean(conversions_mae_scores),
                "conv_rmse_mean": np.mean(conversions_rmse_scores),
                "conv_r2_mean": np.mean(conversions_r2_scores),
                "rate_mae_mean": np.mean(rate_mae_scores),
                "rate_rmse_mean": np.mean(rate_rmse_scores),
                "rate_r2_mean": np.mean(rate_r2_scores),
                "overall_rmse_mean": np.mean(
                    [np.mean(conversions_rmse_scores), np.mean(rate_rmse_scores)]
                ),
                "overall_r2_mean": np.mean(
                    [np.mean(conversions_r2_scores), np.mean(rate_r2_scores)]
                ),
            }
        )

    return (
        pd.DataFrame(rows)
        .sort_values(by=["overall_r2_mean", "overall_rmse_mean"], ascending=[False, True])
        .reset_index(drop=True)
    )


def evaluate_on_holdout(X: pd.DataFrame, y: pd.DataFrame) -> None:
    pipelines = build_model_pipelines()

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
    )

    print("\nDetailed Holdout Evaluation")
    print("=" * 80)

    for name, pipeline in pipelines.items():
        pipeline.fit(X_train, y_train)
        preds = pipeline.predict(X_test)
        pred_df = pd.DataFrame(preds, columns=TARGETS, index=y_test.index)

        conv_mae = mean_absolute_error(y_test["conversions"], pred_df["conversions"])
        conv_rmse = root_mean_squared_error(
            y_test["conversions"],
            pred_df["conversions"],
        )
        conv_r2 = r2_score(y_test["conversions"], pred_df["conversions"])

        rate_mae = mean_absolute_error(
            y_test["conversion_rate"],
            pred_df["conversion_rate"],
        )
        rate_rmse = root_mean_squared_error(
            y_test["conversion_rate"],
            pred_df["conversion_rate"],
        )
        rate_r2 = r2_score(y_test["conversion_rate"], pred_df["conversion_rate"])

        print(f"\nModel: {name}")
        print(
            f"Conversions -> MAE: {conv_mae:.4f} | RMSE: {conv_rmse:.4f} | R2: {conv_r2:.4f}"
        )
        print(
            f"Conversion Rate -> MAE: {rate_mae:.4f} | RMSE: {rate_rmse:.4f} | R2: {rate_r2:.4f}"
        )


def main() -> None:
    X, y = prepare_dataset()

    print("\nCross-Validation Comparison: Campaign Conversion Models")
    print("=" * 80)
    results = evaluate_with_cross_validation(X, y)
    print(results.to_string(index=False))

    evaluate_on_holdout(X, y)

    print("\nRecommended choice:")
    print("Pick the model with the highest overall_r2_mean and the lowest overall_rmse_mean.")
    print("Then use that choice in train_campaign_conversion_model.py.")


if __name__ == "__main__":
    main()