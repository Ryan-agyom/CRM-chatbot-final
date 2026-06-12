from __future__ import annotations

from app.ml.ticket_priority_model import ticket_priority_model
from app.ml.ticket_response_time_model import ticket_response_time_model

class TicketPredictionService:
    @staticmethod
    def predict(payload:dict)->dict:
        priority_prediction = ticket_priority_model.predict(payload)

        response_time_prediction = ticket_response_time_model.predict(
            {
                **payload,
                "predicted_priority":priority_prediction.predicted_priority,
            }
        )
        return{
            "predicted_priority":priority_prediction.predicted_priority,
            "priority_confidence":priority_prediction.confidence,
            "priority_probabilities":priority_prediction.probabilities,
            "predicted_response_time_hours":response_time_prediction.predicted_response_time_hours,
        }
ticket_prediction_service = TicketPredictionService()