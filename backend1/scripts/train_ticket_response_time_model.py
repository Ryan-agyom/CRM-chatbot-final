from __future__ import annotations

from pathlib import Path

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

from app.ml.text_selector import TextSelector


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_ROOT / "data" / "crm_support_tickets.csv"
MODEL_DIR = PROJECT_ROOT / "models"
MODEL_PATH = MODEL_DIR / "ticket_response_time_model.joblib"

FEATURES = ["query_type", "issue_summary", "product", "assigned_department", "predicted_priority"]
TARGET = "response_time_hours"


def build_pipeline() -> Pipeline:
    categorical_features = ["query_type", "product", "assigned_department", "predicted_priority"]

    categorical_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore")),
        ]
    )

    preprocessor = ColumnTransformer(
        transformers=[
            ("cat", categorical_pipeline, categorical_features),
            (
                "text",
                Pipeline(
                    steps=[
                        ("selector", TextSelector("issue_summary")),
                        ("tfidf", TfidfVectorizer(max_features=300, ngram_range=(1, 2))),
                    ]
                ),
                FEATURES,
            ),
        ],
        remainder="drop",
    )

    model = GradientBoostingRegressor(
        n_estimators=200,
        learning_rate=0.05,
        max_depth=3,
        random_state=42,
    )

    return Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("regressor", model),
        ]
    )


def main() -> None:
    df = pd.read_csv(DATA_PATH)
    df = df[df["priority"].notna() & df[TARGET].notna()].copy()

    df["predicted_priority"] = df["priority"].astype(str)

    X = df[FEATURES].copy()
    y = df[TARGET].copy()

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    pipeline = build_pipeline()
    pipeline.fit(X_train, y_train)

    y_pred = pipeline.predict(X_test)

    print("MAE:", round(mean_absolute_error(y_test, y_pred), 4))
    print("RMSE:", round(mean_squared_error(y_test, y_pred) ** 0.5, 4))
    print("R2:", round(r2_score(y_test, y_pred), 4))

    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(
        {
            "model": pipeline,
            "features": FEATURES,
            "target": TARGET,
            "model_name": "GradientBoostingRegressor",
        },
        MODEL_PATH,
    )
    print(f"\nSaved model to: {MODEL_PATH}")


if __name__ == "__main__":
    main()
