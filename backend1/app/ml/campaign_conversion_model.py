from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import joblib
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
MODEL_PATH = PROJECT_ROOT / "models" / "campaign_conversion_model.joblib"


@dataclass
class CampaignConversionPrediction:
    predicted_conversions: int
    predicted_conversion_rate: float


class CampaignConversionModel:
    def __init__(self, model_path: Path | None = None) -> None:
        self.model_path = model_path or MODEL_PATH
        self.bundle: dict[str, Any] | None = None

    def load(self) -> None:
        if not self.model_path.exists():
            raise FileNotFoundError(
                f"Model file not found at {self.model_path}. "
                "Train it first using scripts/train_campaign_conversion_model.py"
            )
        self.bundle = joblib.load(self.model_path)

    def predict(self, payload: dict) -> CampaignConversionPrediction:
        if self.bundle is None:
            self.load()

        assert self.bundle is not None

        model = self.bundle["model"]
        features = self.bundle["features"]

        row = pd.DataFrame(
            [
                {
                    "campaign_type": payload.get("campaign_type", "Unknown"),
                    "target_industry": payload.get("target_industry", "Unknown"),
                    "budget": float(payload.get("budget", 0)),
                    "clicks": float(payload.get("clicks", 0)),
                }
            ]
        )[features]

        prediction = model.predict(row)[0]
        predicted_conversions = int(round(max(float(prediction[0]), 0.0)))
        predicted_conversion_rate = round(max(float(prediction[1]), 0.0), 4)

        return CampaignConversionPrediction(
            predicted_conversions=predicted_conversions,
            predicted_conversion_rate=predicted_conversion_rate,
        )


campaign_conversion_model = CampaignConversionModel()