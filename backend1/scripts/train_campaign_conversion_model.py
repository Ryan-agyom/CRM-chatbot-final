from __future__ import annotations

from pathlib import Path

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error, r2_score, root_mean_squared_error
from sklearn.model_selection import train_test_split
from sklearn.multioutput import MultiOutputRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_ROOT / "data" / "crm_campaigns.csv"
MODEL_DIR = PROJECT_ROOT / "models"
MODEL_PATH = MODEL_DIR / "campaign_conversion_model.joblib"

FEATURES = ["campaign_type", "target_industry", "budget", "clicks"]
TARGETS = ["conversions", "conversion_rate"]


def build_pipeline() -> Pipeline:
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

    preprocessor = ColumnTransformer(
        transformers=[
            ("cat", categorical_pipeline, categorical_features),
            ("num", numeric_pipeline, numeric_features),
        ]
    )

    model = MultiOutputRegressor(
        GradientBoostingRegressor(
            n_estimators=200,
            learning_rate=0.05,
            max_depth=3,
            random_state=42,
        )
    )

    return Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("regressor", model),
        ]
    )


def main() -> None:
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Dataset not found: {DATA_PATH}")

    df = pd.read_csv(DATA_PATH)
    df = df[df[TARGETS].notna().all(axis=1)].copy()

    if df.empty:
        raise ValueError("No trainable rows found for campaign conversion prediction.")

    X = df[FEATURES].copy()
    y = df[TARGETS].copy()

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
    )

    pipeline = build_pipeline()
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

    print("\nModel: GradientBoostingRegressor")
    print(
        f"Conversions -> MAE: {conv_mae:.4f} | RMSE: {conv_rmse:.4f} | R2: {conv_r2:.4f}"
    )
    print(
        f"Conversion Rate -> MAE: {rate_mae:.4f} | RMSE: {rate_rmse:.4f} | R2: {rate_r2:.4f}"
    )

    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(
        {
            "model": pipeline,
            "features": FEATURES,
            "targets": TARGETS,
            "model_name": "MultiOutputRegressor(GradientBoostingRegressor)",
        },
        MODEL_PATH,
    )

    print(f"\nSaved model to: {MODEL_PATH}")


if __name__ == "__main__":
    main()