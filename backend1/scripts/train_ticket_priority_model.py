from __future__ import annotations

from pathlib import Path

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

from app.ml.text_selector import TextSelector


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_ROOT / "data" / "crm_support_tickets.csv"
MODEL_DIR = PROJECT_ROOT / "models"
MODEL_PATH = MODEL_DIR / "ticket_priority_model.joblib"

FEATURES = ["query_type", "issue_summary", "product", "assigned_department"]
TARGET = "priority"


def build_pipeline() -> Pipeline:
    categorical_features = ["query_type", "product", "assigned_department"]

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

    model = GradientBoostingClassifier(
        n_estimators=150,
        learning_rate=0.05,
        max_depth=3,
        random_state=42,
    )

    return Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("classifier", model),
        ]
    )


def main() -> None:
    df = pd.read_csv(DATA_PATH)
    df = df[df[TARGET].notna()].copy()

    X = df[FEATURES].copy()
    y = df[TARGET].copy()

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    pipeline = build_pipeline()
    pipeline.fit(X_train, y_train)

    y_pred = pipeline.predict(X_test)

    print("Accuracy:", round(accuracy_score(y_test, y_pred), 4))
    print("F1 Weighted:", round(f1_score(y_test, y_pred, average="weighted"), 4))
    print("\nClassification Report")
    print(classification_report(y_test, y_pred))
    print("\nConfusion Matrix")
    print(confusion_matrix(y_test, y_pred))

    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(
        {
            "model": pipeline,
            "features": FEATURES,
            "target": TARGET,
            "model_name": "GradientBoostingClassifier",
        },
        MODEL_PATH,
    )
    print(f"\nSaved model to: {MODEL_PATH}")


if __name__ == "__main__":
    main()
