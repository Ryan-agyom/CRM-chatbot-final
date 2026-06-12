from __future__ import annotations

from app.ml.campaign_conversion_model import campaign_conversion_model


class CampaignPredictionService:
    @staticmethod
    def predict(payload: dict) -> dict:
        prediction = campaign_conversion_model.predict(
            {
                "campaign_type": payload.get("campaign_type"),
                "target_industry": payload.get("target_industry"),
                "budget": payload.get("budget"),
                "clicks": payload.get("clicks"),
            }
        )
        return {
            "predicted_conversions": prediction.predicted_conversions,
            "predicted_conversion_rate": prediction.predicted_conversion_rate,
        }


campaign_prediction_service = CampaignPredictionService()