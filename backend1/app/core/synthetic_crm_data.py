from __future__ import annotations

import random

import pandas as pd
from faker import Faker


fake = Faker()
random.seed(42)
Faker.seed(42)

LEAD_SOURCES = [
    "Website",
    "Facebook Ads",
    "Instagram",
    "Google Ads",
    "Referral",
    "LinkedIn",
    "Chatbot",
]

INDUSTRIES = [
    "Retail",
    "Healthcare",
    "Finance",
    "Education",
    "Real Estate",
    "E-commerce",
    "Technology",
]

CAMPAIGN_TYPES = [
    "Email Marketing",
    "Festival Offer",
    "Product Launch",
    "Discount Campaign",
    "Retargeting",
    "Awareness Campaign",
]

QUERY_TYPES = [
    "Billing Inquiry",
    "Technical Support",
    "Refund Request",
    "Product Inquiry",
    "Feature Request",
    "Order Delay",
    "Account Access",
]

ISSUE_SUMMARIES = {
    "Billing Inquiry": [
        "Customer was charged twice for the subscription.",
        "Invoice amount does not match the selected plan.",
        "Customer requested payment receipt.",
        "Refund not received after cancellation.",
    ],
    "Technical Support": [
        "Unable to login to the dashboard.",
        "Application crashes during checkout.",
        "Customer cannot reset password.",
        "Website loads very slowly on mobile devices.",
    ],
    "Refund Request": [
        "Customer wants refund for accidental purchase.",
        "Refund requested for defective product.",
        "Customer cancelled order and requested refund.",
        "Refund delayed beyond expected timeline.",
    ],
    "Product Inquiry": [
        "Customer asked about premium plan features.",
        "Client requested product demo.",
        "Customer wants pricing details.",
        "Inquiry about AI automation capabilities.",
    ],
    "Feature Request": [
        "Customer requested dark mode feature.",
        "User wants WhatsApp integration.",
        "Client suggested multi-language support.",
        "Customer requested advanced analytics dashboard.",
    ],
    "Order Delay": [
        "Customer reported delayed shipment.",
        "Order tracking information not updating.",
        "Package delivery delayed due to logistics issue.",
        "Customer has not received order confirmation.",
    ],
    "Account Access": [
        "Customer account locked after failed login attempts.",
        "Two-factor authentication not working.",
        "User unable to access admin panel.",
        "Password reset email not received.",
    ],
}

TICKET_STATUS = ["Open", "Closed", "Pending", "Resolved"]
PRODUCTS = [
    "CRM Suite",
    "AI Assistant",
    "Analytics Dashboard",
    "Marketing Tool",
    "Automation Platform",
]
DEPARTMENTS = ["Support", "Technical", "Billing", "Sales"]


def weighted_choice(weight_map: dict[str, float]) -> str:
    items = list(weight_map.keys())
    weights = list(weight_map.values())
    return random.choices(items, weights=weights, k=1)[0]


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(value, high))


def infer_lead_status(
    *,
    lead_source: str,
    budget: int,
    interest_level: str,
    industry: str,
) -> str:
    score = 0

    source_score = {
        "Referral": 28,
        "LinkedIn": 22,
        "Website": 18,
        "Google Ads": 16,
        "Chatbot": 14,
        "Facebook Ads": 10,
        "Instagram": 8,
    }
    score += source_score.get(lead_source, 10)

    if budget >= 35000:
        score += 28
    elif budget >= 20000:
        score += 20
    elif budget >= 10000:
        score += 12
    else:
        score += 5

    interest_score = {
        "High": 28,
        "Medium": 15,
        "Low": 4,
    }
    score += interest_score.get(interest_level, 8)

    industry_score = {
        "Technology": 10,
        "Finance": 9,
        "Healthcare": 8,
        "E-commerce": 8,
        "Education": 6,
        "Retail": 5,
        "Real Estate": 4,
    }
    score += industry_score.get(industry, 5)

    score += random.randint(-10, 10)

    if score >= 78:
        return weighted_choice(
            {
                "Converted": 0.55,
                "Qualified": 0.35,
                "New": 0.10,
            }
        )
    if score >= 55:
        return weighted_choice(
            {
                "Qualified": 0.55,
                "Converted": 0.15,
                "New": 0.25,
                "Lost": 0.05,
            }
        )
    if score >= 35:
        return weighted_choice(
            {
                "New": 0.55,
                "Qualified": 0.20,
                "Lost": 0.25,
            }
        )
    return weighted_choice(
        {
            "Lost": 0.65,
            "New": 0.25,
            "Qualified": 0.10,
        }
    )


def infer_campaign_performance(
    *,
    campaign_type: str,
    target_industry: str,
    budget: int,
    status: str,
) -> dict[str, float | int]:
    base_conversion = {
        "Email Marketing": 6.5,
        "Festival Offer": 8.0,
        "Product Launch": 5.5,
        "Discount Campaign": 9.0,
        "Retargeting": 11.0,
        "Awareness Campaign": 3.5,
    }.get(campaign_type, 5.0)

    industry_modifier = {
        "Technology": 2.2,
        "E-commerce": 2.5,
        "Finance": 1.5,
        "Healthcare": 1.2,
        "Education": 0.8,
        "Retail": 1.0,
        "Real Estate": 0.4,
    }.get(target_industry, 0.5)

    budget_modifier = 0
    if budget >= 70000:
        budget_modifier = 2.0
    elif budget >= 40000:
        budget_modifier = 1.2
    elif budget >= 20000:
        budget_modifier = 0.5

    status_modifier = {
        "Completed": 1.4,
        "Active": 0.7,
        "Paused": -1.0,
    }.get(status, 0)

    conversion_rate = base_conversion + industry_modifier + budget_modifier + status_modifier + random.uniform(-1.5, 1.5)
    conversion_rate = clamp(conversion_rate, 1.0, 25.0)

    impressions = int(clamp(budget * random.uniform(2.5, 8.0), 1000, 150000))
    ctr = clamp(random.uniform(0.015, 0.09), 0.01, 0.12)
    clicks = int(impressions * ctr)
    conversions = int(clicks * (conversion_rate / 100))

    return {
        "impressions": impressions,
        "clicks": clicks,
        "conversions": conversions,
        "conversion_rate": round(conversion_rate, 2),
    }


def infer_ticket_priority(
    *,
    query_type: str,
    issue_summary: str,
    product: str,
    assigned_department: str,
) -> str:
    text = issue_summary.lower()
    score = 0

    query_score = {
        "Account Access": 30,
        "Technical Support": 24,
        "Refund Request": 18,
        "Billing Inquiry": 12,
        "Order Delay": 10,
        "Product Inquiry": 6,
        "Feature Request": 4,
    }
    score += query_score.get(query_type, 8)

    department_score = {
        "Technical": 10,
        "Billing": 7,
        "Support": 5,
        "Sales": 2,
    }
    score += department_score.get(assigned_department, 3)

    product_score = {
        "CRM Suite": 7,
        "Automation Platform": 6,
        "AI Assistant": 5,
        "Analytics Dashboard": 4,
        "Marketing Tool": 3,
    }
    score += product_score.get(product, 3)

    urgent_keywords = [
        "locked",
        "cannot login",
        "unable to login",
        "crashes",
        "not working",
        "failed",
        "admin panel",
        "charged twice",
        "refund delayed",
    ]
    medium_keywords = [
        "slowly",
        "reset password",
        "delayed",
        "tracking",
        "payment",
        "invoice",
    ]

    if any(keyword in text for keyword in urgent_keywords):
        score += 25
    elif any(keyword in text for keyword in medium_keywords):
        score += 12

    score += random.randint(-6, 6)

    if score >= 55:
        return weighted_choice({"Critical": 0.65, "High": 0.35})
    if score >= 40:
        return weighted_choice({"High": 0.65, "Critical": 0.10, "Medium": 0.25})
    if score >= 22:
        return weighted_choice({"Medium": 0.70, "High": 0.20, "Low": 0.10})
    return weighted_choice({"Low": 0.70, "Medium": 0.25, "High": 0.05})


def infer_response_time_hours(
    *,
    priority: str,
    query_type: str,
    assigned_department: str,
) -> int:
    base_by_priority = {
        "Critical": (1, 6),
        "High": (4, 16),
        "Medium": (12, 36),
        "Low": (24, 72),
    }

    low, high = base_by_priority.get(priority, (12, 36))

    if query_type == "Account Access":
        low = max(1, low - 2)
        high = max(low + 1, high - 6)
    elif query_type == "Feature Request":
        low += 8
        high += 12

    if assigned_department == "Technical":
        high += 4
    elif assigned_department == "Sales":
        high += 8

    return random.randint(low, high)


def infer_ticket_status(*, priority: str, response_time_hours: int) -> str:
    if priority in {"Critical", "High"} and response_time_hours <= 12:
        return weighted_choice({"Resolved": 0.20, "Pending": 0.35, "Open": 0.45})
    if response_time_hours >= 40:
        return weighted_choice({"Pending": 0.45, "Open": 0.30, "Closed": 0.25})
    return weighted_choice({"Open": 0.30, "Resolved": 0.35, "Closed": 0.20, "Pending": 0.15})


def infer_satisfaction_score(
    *,
    priority: str,
    response_time_hours: int,
    status: str,
) -> int:
    score = 3

    if priority == "Critical":
        score -= 1
    elif priority == "Low":
        score += 1

    if response_time_hours <= 6:
        score += 1
    elif response_time_hours >= 36:
        score -= 1

    if status in {"Resolved", "Closed"}:
        score += 1
    elif status == "Open":
        score -= 1

    score += random.choice([-1, 0, 0, 1])
    return int(clamp(score, 1, 5))


def build_synthetic_dataset(*, leads: int, campaigns: int, tickets: int) -> dict[str, pd.DataFrame]:
    lead_rows = []
    for index in range(leads):
        industry = random.choice(INDUSTRIES)
        lead_source = random.choice(LEAD_SOURCES)
        budget = random.randint(1000, 50000)
        interest_level = random.choices(
            ["Low", "Medium", "High"],
            weights=[0.25, 0.45, 0.30],
            k=1,
        )[0]
        status = infer_lead_status(
            lead_source=lead_source,
            budget=budget,
            interest_level=interest_level,
            industry=industry,
        )

        lead_rows.append(
            {
                "lead_id": index + 1,
                "customer_name": fake.name(),
                "email": fake.email(),
                "phone": fake.phone_number(),
                "company": fake.company(),
                "industry": industry,
                "lead_source": lead_source,
                "budget": budget,
                "interest_level": interest_level,
                "status": status,
                "city": fake.city(),
                "created_at": fake.date_this_year(),
            }
        )

    campaign_rows = []
    for index in range(campaigns):
        campaign_type = random.choice(CAMPAIGN_TYPES)
        target_industry = random.choice(INDUSTRIES)
        budget = random.randint(5000, 100000)
        status = weighted_choice({"Active": 0.45, "Paused": 0.15, "Completed": 0.40})

        performance = infer_campaign_performance(
            campaign_type=campaign_type,
            target_industry=target_industry,
            budget=budget,
            status=status,
        )

        campaign_rows.append(
            {
                "campaign_id": index + 1,
                "campaign_name": f"{campaign_type} {index + 1}",
                "campaign_type": campaign_type,
                "target_industry": target_industry,
                "budget": budget,
                "clicks": performance["clicks"],
                "impressions": performance["impressions"],
                "conversions": performance["conversions"],
                "conversion_rate": performance["conversion_rate"],
                "status": status,
                "launch_date": fake.date_this_year(),
            }
        )

    ticket_rows = []
    for index in range(tickets):
        query_type = random.choice(QUERY_TYPES)
        issue_summary = random.choice(ISSUE_SUMMARIES[query_type])

        if query_type in {"Technical Support", "Account Access"}:
            assigned_department = "Technical"
        elif query_type in {"Billing Inquiry", "Refund Request"}:
            assigned_department = "Billing"
        elif query_type == "Product Inquiry":
            assigned_department = "Sales"
        else:
            assigned_department = "Support"

        if query_type in {"Technical Support", "Account Access"}:
            product = random.choice(["CRM Suite", "AI Assistant", "Automation Platform"])
        elif query_type in {"Billing Inquiry", "Refund Request"}:
            product = random.choice(["CRM Suite", "Marketing Tool", "Analytics Dashboard"])
        else:
            product = random.choice(PRODUCTS)

        priority = infer_ticket_priority(
            query_type=query_type,
            issue_summary=issue_summary,
            product=product,
            assigned_department=assigned_department,
        )

        response_time_hours = infer_response_time_hours(
            priority=priority,
            query_type=query_type,
            assigned_department=assigned_department,
        )

        status = infer_ticket_status(
            priority=priority,
            response_time_hours=response_time_hours,
        )

        satisfaction_score = infer_satisfaction_score(
            priority=priority,
            response_time_hours=response_time_hours,
            status=status,
        )

        ticket_rows.append(
            {
                "ticket_id": index + 1,
                "customer_name": fake.name(),
                "email": fake.email(),
                "query_type": query_type,
                "issue_summary": issue_summary,
                "product": product,
                "priority": priority,
                "status": status,
                "assigned_department": assigned_department,
                "response_time_hours": response_time_hours,
                "satisfaction_score": satisfaction_score,
                "created_at": fake.date_this_year(),
            }
        )

    return {
        "leads": pd.DataFrame(lead_rows),
        "campaigns": pd.DataFrame(campaign_rows),
        "tickets": pd.DataFrame(ticket_rows),
    }