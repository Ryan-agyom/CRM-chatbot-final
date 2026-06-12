from __future__ import annotations

from pathlib import Path

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import ExtraTreesClassifier, GradientBoostingClassifier, RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, f1_score, precision_score, recall_score
from sklearn.model_selection import StratifiedKFold, cross_validate, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.tree import DecisionTreeClassifier

from app.ml.text_selector import TextSelector


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_ROOT / "data" / "crm_support_tickets.csv"

FEATURES = ["query_type", "issue_summary", "product", "assigned_department"]
TARGET = "priority"


def build_preprocessor() -> ColumnTransformer:
    categorical_features = ["query_type", "product", "assigned_department"]

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
        "logistic_regression": LogisticRegression(max_iter=1000, class_weight="balanced"),
        "decision_tree": DecisionTreeClassifier(
            max_depth=6,
            min_samples_leaf=3,
            class_weight="balanced",
            random_state=42,
        ),
        "random_forest": RandomForestClassifier(
            n_estimators=200,
            max_depth=8,
            min_samples_leaf=3,
            class_weight="balanced",
            random_state=42,
        ),
        "extra_trees": ExtraTreesClassifier(
            n_estimators=200,
            max_depth=8,
            min_samples_leaf=3,
            class_weight="balanced",
            random_state=42,
        ),
        "gradient_boosting": GradientBoostingClassifier(
            n_estimators=150,
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
                ("classifier", model),
            ]
        )
    return pipelines


def evaluate_with_cross_validation(X: pd.DataFrame, y: pd.Series) -> pd.DataFrame:
    pipelines = build_model_pipelines()
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

    scoring = {
        "accuracy": "accuracy",
        "precision": "precision_weighted",
        "recall": "recall_weighted",
        "f1": "f1_weighted",
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
                "cv_accuracy_mean": scores["test_accuracy"].mean(),
                "cv_precision_mean": scores["test_precision"].mean(),
                "cv_recall_mean": scores["test_recall"].mean(),
                "cv_f1_mean": scores["test_f1"].mean(),
            }
        )

    return pd.DataFrame(rows).sort_values(by="cv_f1_mean", ascending=False).reset_index(drop=True)


def evaluate_on_holdout(X: pd.DataFrame, y: pd.Series) -> None:
    pipelines = build_model_pipelines()

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y,
    )

    print("\nDetailed Holdout Evaluation")
    print("=" * 60)

    for name, pipeline in pipelines.items():
        pipeline.fit(X_train, y_train)
        y_pred = pipeline.predict(X_test)

        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred, average="weighted", zero_division=0)
        recall = recall_score(y_test, y_pred, average="weighted", zero_division=0)
        f1 = f1_score(y_test, y_pred, average="weighted", zero_division=0)

        print(f"\nModel: {name}")
        print(f"Accuracy : {accuracy:.4f}")
        print(f"Precision: {precision:.4f}")
        print(f"Recall   : {recall:.4f}")
        print(f"F1 Score : {f1:.4f}")
        print("\nClassification Report")
        print(classification_report(y_test, y_pred, zero_division=0))


def main() -> None:
    df = pd.read_csv(DATA_PATH)
    df = df[df[TARGET].notna()].copy()

    if df.empty:
        raise ValueError("No trainable rows found for priority prediction.")

    X = df[FEATURES].copy()
    y = df[TARGET].copy()

    print("\nCross-Validation Comparison: Ticket Priority Models")
    print("=" * 60)
    results = evaluate_with_cross_validation(X, y)
    print(results.to_string(index=False))

    evaluate_on_holdout(X, y)

    print("\nRecommended choice:")
    print("Pick the model with the highest weighted F1 score.")


if __name__ == "__main__":
    main()
