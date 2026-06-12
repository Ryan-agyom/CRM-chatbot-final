from __future__ import annotations

from pathlib import Path

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_ROOT / "data" / "crm_leads.csv"
MODEL_DIR = PROJECT_ROOT / "models"
MODEL_PATH = MODEL_DIR / "lead_status_model.joblib"

FEATURES = ["lead_source", "budget", "interest_level", "industry"]
TARGET = "target_status"


def build_target(frame: pd.DataFrame) -> pd.DataFrame:
    df = frame.copy()

    mapping = {
        "Qualified": "Qualified",
        "Converted": "Qualified",
        "Lost": "Lost",
    }

    df[TARGET] = df["status"].map(mapping)
    df = df[df[TARGET].notna()].copy()

    return df


def build_pipeline() -> Pipeline:
    categorical_features = ["lead_source", "interest_level", "industry"]
    numeric_features = ["budget"]

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

    preprocessor = ColumnTransformer(
        transformers=[
            ("cat", categorical_pipeline, categorical_features),
            ("num", numeric_pipeline, numeric_features),
        ]
    )

    model = RandomForestClassifier(
        n_estimators=150,
        min_samples_leaf= 5,
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
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Dataset not found: {DATA_PATH}")

    df = pd.read_csv(DATA_PATH)
    df = build_target(df)

    if df.empty:
        raise ValueError(
            "No trainable rows found. Your dataset must contain some "
            "status values in {'Qualified', 'Converted', 'Lost'}."
        )

    X = df[FEATURES].copy()
    y = df[TARGET].copy()

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y,
    )

    pipeline = build_pipeline()
    pipeline.fit(X_train, y_train)

    y_pred = pipeline.predict(X_test)

    print("\nModel: RandomForestClassifier")
    print(f"Accuracy : {accuracy_score(y_test, y_pred):.4f}")
    print(f"Precision: {precision_score(y_test, y_pred, average='weighted', zero_division=0):.4f}")
    print(f"Recall   : {recall_score(y_test, y_pred, average='weighted', zero_division=0):.4f}")
    print(f"F1 Score : {f1_score(y_test, y_pred, average='weighted', zero_division=0):.4f}")

    print("\nClassification Report")
    print(classification_report(y_test, y_pred, zero_division=0))

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