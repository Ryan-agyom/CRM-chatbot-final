from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import joblib
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
MODEL_DIR = PROJECT_ROOT / "models"
MODEL_PATH = MODEL_DIR / "lead_status_model.joblib"


@dataclass
class LeadStatusPrediction:
    predicted_status: str
    confidence: float
    probabilities: dict[str, float]


class LeadStatusModel:
    def __init__(self, model_path: Path | None = None) -> None:
        self.model_path = model_path or MODEL_PATH
        self.bundle: dict[str, Any] | None = None

    def load(self) -> None:
        if not self.model_path.exists():
            raise FileNotFoundError(
                f"Model file not found at {self.model_path}. "
                "Train it first using scripts/train_lead_status_model.py"
            )
        self.bundle = joblib.load(self.model_path)

    def predict(self, payload: dict) -> LeadStatusPrediction:
        if self.bundle is None:
            self.load()

        assert self.bundle is not None

        model = self.bundle["model"]
        features = self.bundle["features"]

        row = pd.DataFrame(
            [
                {
                    "lead_source": payload.get("lead_source", "Unknown"),
                    "budget": float(payload.get("budget", 0)),
                    "interest_level": payload.get("interest_level", "Low"),
                    "industry": payload.get("industry", "Unknown"),
                }
            ]
        )[features]

        predicted_status = str(model.predict(row)[0])

        if hasattr(model, "predict_proba"):
            probabilities_array = model.predict_proba(row)[0]
            class_names = [str(label) for label in model.classes_]
            probabilities = {
                label: round(float(prob), 4)
                for label, prob in zip(class_names, probabilities_array)
            }
            confidence = max(probabilities.values())
        else:
            probabilities = {predicted_status: 1.0}
            confidence = 1.0

        return LeadStatusPrediction(
            predicted_status=predicted_status,
            confidence=round(confidence, 4),
            probabilities=probabilities,
        )

lead_status_model = LeadStatusModel()