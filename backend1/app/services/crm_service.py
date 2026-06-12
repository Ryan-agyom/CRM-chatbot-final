from __future__ import annotations

from uuid import uuid4

from app.core.crm_repository import crm_repository
from app.core.lead_scoring import score_lead
from app.core.synthetic_crm_data import build_synthetic_dataset

class CRMService:
    @staticmethod
    def _serialize_sample(frame) -> dict | None:
        if frame.empty:
            return None
        record = frame.head(1).copy()
        for column in record.columns:
            if hasattr(record[column], "dt"):
                try:
                    record[column] = record[column].dt.strftime("%Y-%m-%d")
                except Exception:
                    pass
        sample = record.to_dict(orient="records")[0]
        for key, value in sample.items():
            if hasattr(value, "isoformat"):
                sample[key] = value.isoformat()
        return sample

    @staticmethod
    def get_overview() -> dict:
        return {
            "module": "crm",
            "sections": ["sales", "marketing", "support", "analytics"],
            "independence": "The CRM module is isolated from the core chatbot module.",
        }

    @staticmethod
    def list_leads() -> list[dict]:
        return crm_repository.list_leads()

    @staticmethod
    def list_campaigns() -> list[dict]:
        return crm_repository.list_campaigns()

    @staticmethod
    def list_support_tickets() -> list[dict]:
        return crm_repository.list_tickets()

    @staticmethod
    def create_lead(payload: dict) -> dict:
        return crm_repository.create_lead(payload)

    @staticmethod
    def update_lead(identifier: dict, updates: dict) -> dict | None:
        return crm_repository.update_lead(identifier, updates)

    @staticmethod
    def delete_lead(identifier: dict) -> dict | None:
        return crm_repository.delete_lead(identifier)

    @staticmethod
    def qualify_lead(payload: dict) -> dict:
        score = score_lead(payload)
        return {
            "score": score,
            "category": "hot" if score >= 80 else "warm" if score >= 50 else "cold",
            "criteria": {
                "budget": payload["budget"],
                "interestLevel": payload["interest_level"],
                "companySize": payload["company_size"],
                "purchaseTimeline": payload["purchase_timeline"],
            },
        }

    @staticmethod
    def schedule_appointment(payload: dict) -> dict:
        return {
            "id": str(uuid4()),
            "customerName": payload["customer_name"],
            "type": payload.get("type", "demo"),
            "scheduledFor": payload["scheduled_for"],
            "reminderEnabled": payload.get("reminder_enabled", True),
        }

    @staticmethod
    def create_campaign(payload: dict) -> dict:
        return crm_repository.create_campaign(payload)

    @staticmethod
    def update_campaign(identifier: dict, updates: dict) -> dict | None:
        return crm_repository.update_campaign(identifier, updates)

    @staticmethod
    def delete_campaign(identifier: dict) -> dict | None:
        return crm_repository.delete_campaign(identifier)

    @staticmethod
    def create_support_ticket(payload: dict) -> dict:
        return crm_repository.create_ticket(payload)

    @staticmethod
    def update_support_ticket(identifier: dict, updates: dict) -> dict | None:
        return crm_repository.update_ticket(identifier, updates)

    @staticmethod
    def delete_support_ticket(identifier: dict) -> dict | None:
        return crm_repository.delete_ticket(identifier)

    @staticmethod
    def get_insights() -> dict:
        leads = crm_repository.list_leads()
        campaigns = crm_repository.list_campaigns()
        tickets = crm_repository.list_tickets()

        common_complaints = {}
        for ticket in tickets:
            issue = ticket["query_type"]
            common_complaints[issue] = common_complaints.get(issue, 0) + 1

        sorted_complaints = sorted(
            common_complaints.items(),
            key=lambda item: (-item[1], item[0]),
        )
        likely_to_convert = sum(1 for lead in leads if lead["status"] in {"Qualified", "Converted"})
        open_tickets = sum(1 for ticket in tickets if ticket["status"] == "Open")
        top_products = {}
        for ticket in tickets:
            product = ticket["product"]
            top_products[product] = top_products.get(product, 0) + 1

        trending_products = [
            product
            for product, _count in sorted(top_products.items(), key=lambda item: (-item[1], item[0]))[:5]
        ]

        return {
            "customerInsights": {
                "leadCount": len(leads),
                "commonComplaints": [issue for issue, _count in sorted_complaints[:6]],
                "activeCampaigns": sum(1 for campaign in campaigns if campaign["status"] == "Active"),
            },
            "predictiveAnalysis": {
                "likelyToConvert": likely_to_convert,
                "likelyToChurn": "medium-risk" if open_tickets > 5 else "low-risk",
                "trendingProducts": trending_products,
            },
        }

    @staticmethod
    def seed_synthetic_crm_data(*, leads: int, campaigns: int, tickets: int) -> dict:
        dataset = build_synthetic_dataset(leads=leads, campaigns=campaigns, tickets=tickets)
        counts = crm_repository.replace_all(
            leads=dataset["leads"],
            campaigns=dataset["campaigns"],
            tickets=dataset["tickets"],
        )

        return {
            "counts": counts,
            "sample": {
                "lead": CRMService._serialize_sample(dataset["leads"]),
                "campaign": CRMService._serialize_sample(dataset["campaigns"]),
                "ticket": CRMService._serialize_sample(dataset["tickets"]),
            },
        }


crm_service = CRMService()
