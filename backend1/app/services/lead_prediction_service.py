from __future__ import annotations
from app.ml.lead_status_model import lead_status_model

class LeadPredictionService:
    @staticmethod
    def predict(payload:dict)->dict:
        prediction = lead_status_model.predict(
            {
                "lead_source":payload.get("lead_source"),
                "budget":payload.get("budget"),
                "interest_level":payload.get("interest_level"),
                "industry":payload.get("industry"),
            }
        )
        return{
            "predicted_status":prediction.predicted_status,
            "confidence":prediction.confidence,
            "probabilities":prediction.probabilities,
        }

lead_prediction_service = LeadPredictionService()