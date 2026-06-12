from __future__ import annotations

from pathlib import Path

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import ExtraTreesRegressor, GradientBoostingRegressor, RandomForestRegressor
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import KFold, cross_validate, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.tree import DecisionTreeRegressor

from app.ml.text_selector import TextSelector


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_ROOT / "data" / "crm_support_tickets.csv"

FEATURES = ["query_type", "issue_summary", "product", "assigned_department", "predicted_priority"]
TARGET = "response_time_hours"


def build_preprocessor() -> ColumnTransformer:
    categorical_features = ["query_type", "product", "assigned_department", "predicted_priority"]

    categorical_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore")),
        ]
    )

    text_pipeline = Pipeline(
        steps=[
            ("selector", TextSelector("issue_summary")),
            ("tfidf", TfidfVectorizer(max_features=300, ngram_range=(1, 2))),
        ]
    )

    return ColumnTransformer(
        transformers=[
            ("cat", categorical_pipeline, categorical_features),
            ("text", text_pipeline, FEATURES),
        ],
        remainder="drop",
    )


def build_model_pipelines() -> dict[str, Pipeline]:
    preprocessor = build_preprocessor()

    models = {
        "ridge": Ridge(alpha=1.0),
        "decision_tree_regressor": DecisionTreeRegressor(
            max_depth=6,
            min_samples_leaf=3,
            random_state=42,
        ),
        "random_forest_regressor": RandomForestRegressor(
            n_estimators=200,
            max_depth=8,
            min_samples_leaf=3,
            random_state=42,
            n_jobs=-1,
        ),
        "extra_trees_regressor": ExtraTreesRegressor(
            n_estimators=200,
            max_depth=8,
            min_samples_leaf=3,
            random_state=42,
            n_jobs=-1,
        ),
        "gradient_boosting_regressor": GradientBoostingRegressor(
            n_estimators=200,
            learning_rate=0.05,
            max_depth=3,
            random_state=42,
        ),
    }

    pipelines = {}
    for name, model in models.items():
        pipelines[name] = Pipeline(
            steps=[
                ("preprocessor", preprocessor),
                ("regressor", model),
            ]
        )
    return pipelines


def evaluate_with_cross_validation(X: pd.DataFrame, y: pd.Series) -> pd.DataFrame:
    pipelines = build_model_pipelines()
    cv = KFold(n_splits=5, shuffle=True, random_state=42)

    scoring = {
        "mae": "neg_mean_absolute_error",
        "rmse": "neg_root_mean_squared_error",
        "r2": "r2",
    }

    rows = []

    for name, pipeline in pipelines.items():
        scores = cross_validate(
            pipeline,
            X,
            y,
            cv=cv,
            scoring=scoring,
            n_jobs=-1,
        )

        rows.append(
            {
                "model": name,
                "cv_mae_mean": -scores["test_mae"].mean(),
                "cv_rmse_mean": -scores["test_rmse"].mean(),
                "cv_r2_mean": scores["test_r2"].mean(),
            }
        )

    return pd.DataFrame(rows).sort_values(by=["cv_mae_mean", "cv_rmse_mean"], ascending=[True, True]).reset_index(drop=True)


def evaluate_on_holdout(X: pd.DataFrame, y: pd.Series) -> None:
    pipelines = build_model_pipelines()

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
    )

    print("\nDetailed Holdout Evaluation")
    print("=" * 60)

    for name, pipeline in pipelines.items():
        pipeline.fit(X_train, y_train)
        y_pred = pipeline.predict(X_test)

        mae = mean_absolute_error(y_test, y_pred)
        rmse = mean_squared_error(y_test, y_pred) ** 0.5
        r2 = r2_score(y_test, y_pred)

        print(f"\nModel: {name}")
        print(f"MAE : {mae:.4f}")
        print(f"RMSE: {rmse:.4f}")
        print(f"R2  : {r2:.4f}")


def main() -> None:
    df = pd.read_csv(DATA_PATH)
    df = df[df["priority"].notna() & df[TARGET].notna()].copy()

    if df.empty:
        raise ValueError("No trainable rows found for response time prediction.")

    df["predicted_priority"] = df["priority"].astype(str)

    X = df[FEATURES].copy()
    y = df[TARGET].copy()

    print("\nCross-Validation Comparison: Ticket Response Time Models")
    print("=" * 60)
    results = evaluate_with_cross_validation(X, y)
    print(results.to_string(index=False))

    evaluate_on_holdout(X, y)

    print("\nRecommended choice:")
    print("Prefer the model with the lowest MAE and RMSE, and a better R2.")


if __name__ == "__main__":
    main()
