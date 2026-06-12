from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import joblib
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
MODEL_PATH = PROJECT_ROOT / "models" / "ticket_response_time_model.joblib"


@dataclass
class TicketResponseTimePrediction:
    predicted_response_time_hours: float


class TicketResponseTimeModel:
    def __init__(self, model_path: Path | None = None) -> None:
        self.model_path = model_path or MODEL_PATH
        self.bundle: dict[str, Any] | None = None

    def load(self) -> None:
        if not self.model_path.exists():
            raise FileNotFoundError(f"Model file not found at {self.model_path}")
        self.bundle = joblib.load(self.model_path)

    def predict(self, payload: dict) -> TicketResponseTimePrediction:
        if self.bundle is None:
            self.load()

        model = self.bundle["model"]
        features = self.bundle["features"]

        row = pd.DataFrame(
            [{
                "query_type": payload.get("query_type", "Unknown"),
                "issue_summary": payload.get("issue_summary", ""),
                "product": payload.get("product", "Unknown"),
                "assigned_department": payload.get("assigned_department", "Support"),
                "predicted_priority": payload.get("predicted_priority", "Medium"),
            }]
        )[features]

        predicted_hours = float(model.predict(row)[0])

        return TicketResponseTimePrediction(
            predicted_response_time_hours=round(max(predicted_hours, 0.0), 2)
        )


ticket_response_time_model = TicketResponseTimeModel()