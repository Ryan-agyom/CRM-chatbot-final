from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import joblib
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
MODEL_PATH = PROJECT_ROOT / "models" / "ticket_priority_model.joblib"

@dataclass
class TicketPriorityPrediction:
    predicted_priority:str
    confidence:float
    probabilities:dict[str,float]

class TicketPriorityModel:
    def __init__(self,model_path:Path|None=None)->None:
        self.model_path = model_path or MODEL_PATH
        self.bundle: dict[str,Any] | None = None

    def load(self)->None:
        if not self.model_path.exists():
            raise FileNotFoundError(f"Model file not found at {self.model_path}")
        self.bundle = joblib.load(self.model_path)

    def predict(self,payload:dict)->TicketPriorityPrediction:
        if self.bundle is None:
            self.load()
        
        model = self.bundle["model"]
        features = self.bundle["features"]

        row = pd.DataFrame(
            [{
                "query_type":payload.get("query_type","Unknown"),
                "issue_summary":payload.get("issue_summary",""),
                "product":payload.get("product","Unknown"),
                "assigned_department":payload.get("assigned_department","Support"),
            }]
        )[features]

        predicted_priority = str(model.predict(row)[0])

        if hasattr(model,"predict_proba"):
            probs = model.predict_proba(row)[0]
            labels = [str(label) for label in model.classes_]
            probabilities = {
                label: round(float(prob),4)
                for label,prob in zip(labels,probs)
            }
            confidence = max(probabilities.values())
        else:
            probabilities = {predicted_priority:1.0}
            confidence = 1.0

        return TicketPriorityPrediction(
            predicted_priority=predicted_priority,
            confidence = round(confidence,4),
            probabilities = probabilities,
        )
ticket_priority_model = TicketPriorityModel()