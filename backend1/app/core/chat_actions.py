from __future__ import annotations

import re

from app.services.crm_service import crm_service
from app.services.lead_prediction_service import lead_prediction_service
EMAIL_REGEX = re.compile(r"[\w.\-+]+@[\w.\-]+\.\w+")
PHONE_REGEX = re.compile(r"(\+?\d[\d\s\-()]{7,}\d)")


QUERY_TYPE_NORMALIZATION = {
    "billing inquiry": "Billing Inquiry",
    "technical support": "Technical Support",
    "refund request": "Refund Request",
    "product inquiry": "Product Inquiry",
    "feature request": "Feature Request",
    "order delay": "Order Delay",
    "account access": "Account Access",
}

LEAD_INTEREST_LEVELS = {"low": "Low", "medium": "Medium", "high": "High"}
TICKET_PRIORITIES = {"low": "Low", "medium": "Medium", "high": "High"}
LEAD_STATUSES = {
    "new": "New",
    "qualified": "Qualified",
    "converted": "Converted",
    "lost": "Lost",
}
TICKET_STATUSES = {
    "open": "Open",
    "in progress": "In Progress",
    "closed": "Closed",
    "resolved": "Resolved",
}
CAMPAIGN_STATUSES = {
    "active": "Active",
    "paused": "Paused",
    "completed": "Completed",
    "draft": "Draft",
}
CAMPAIGN_TYPE_NORMALIZATION = {
    "email marketing": "Email Marketing",
    "social media": "Social Media",
    "ppc": "PPC",
    "search ads": "PPC",
    "content marketing": "Content Marketing",
    "webinar": "Webinar",
}


def try_handle_chat_action(message: str) -> str | None:
    normalized = " ".join(message.lower().split())

    intent = _detect_action_intent(normalized)
    if intent is None:
        return None
    action, entity = intent
    if action == "create" and entity == "lead":
        return _handle_lead_creation(message)
    if action == "create" and entity == "ticket":
        return _handle_ticket_creation(message)
    if action == "create" and entity == "campaign":
        return _handle_campaign_creation(message)
    if action == "update" and entity == "lead":
        return _handle_lead_update(message)
    if action == "update" and entity == "ticket":
        return _handle_ticket_update(message)
    if action == "update" and entity == "campaign":
        return _handle_campaign_update(message)
    if action == "delete" and entity == "lead":
        return _handle_lead_delete(message)
    if action == "delete" and entity == "ticket":
        return _handle_ticket_delete(message)
    if action == "delete" and entity == "campaign":
        return _handle_campaign_delete(message)

    return None


def is_mutation_request(message: str) -> bool:
    normalized = " ".join(message.lower().split())
    return _detect_action_intent(normalized) is not None


def _detect_action_intent(message: str) -> tuple[str, str] | None:
    action_aliases = {
        "create": ("create", "add", "new", "insert", "raise"),
        "update": ("update", "change", "edit", "modify", "set"),
        "delete": ("delete", "remove", "drop"),
    }
    entity_aliases = {
        "lead": ("lead", "leads"),
        "ticket": ("ticket", "tickets", "support ticket", "support tickets"),
        "campaign": ("campaign", "campaigns"),
    }

    if _looks_like_question(message) and not any(verb in message for verb in ("delete", "remove", "update", "change", "edit", "modify", "create", "add", "insert", "raise")):
        return None

    for action, verbs in action_aliases.items():
        for entity, names in entity_aliases.items():
            if not any(re.search(rf"\b{re.escape(verb)}\b", message) for verb in verbs):
                continue
            if _matches_action_entity_pair(message, verbs, names):
                return action, entity
    return None


def _looks_like_question(message: str) -> bool:
    question_starters = ("what", "which", "who", "when", "where", "why", "how", "show", "tell", "list")
    return message.endswith("?") or message.startswith(question_starters)


def _matches_action_entity_pair(message: str, verbs: tuple[str, ...], names: tuple[str, ...]) -> bool:
    for verb in verbs:
        for name in names:
            if re.search(rf"\b{re.escape(verb)}\s+(?:a|an|the)?\s*{re.escape(name)}\b", message):
                return True
            if re.search(rf"\b{re.escape(name)}\s+(?:to\s+)?{re.escape(verb)}\b", message):
                return True

    if any(name in message for name in names):
        return any(
            phrase in message
            for phrase in (
                "for lead",
                "lead for",
                "for ticket",
                "ticket for",
                "for campaign",
                "campaign for",
            )
        ) and any(re.search(rf"\b{re.escape(verb)}\b", message) for verb in verbs)

    return False


def _extract_named_field(message: str, *field_names: str) -> str | None:
    for field_name in field_names:
        candidate_patterns = {
            field_name,
            field_name.replace("_", " "),
            field_name.replace("_", ""),
        }
        for candidate in candidate_patterns:
            pattern = re.compile(
                rf"\b{re.escape(candidate)}\b\s*(?:is|=|:|to)?\s*['\"]?([^,;\n]+?)['\"]?(?=(?:\s+\w+(?:\s+\w+)?\s*(?:is|=|:|to))|[,;\n]|$)",
                re.IGNORECASE,
            )
            match = pattern.search(message)
            if match:
                return match.group(1).strip(" .")
    return None


def _extract_email(message: str) -> str | None:
    match = EMAIL_REGEX.search(message)
    return match.group(0) if match else None


def _extract_phone(message: str) -> str | None:
    match = PHONE_REGEX.search(message)
    return match.group(1).strip() if match else None


def _extract_number_after_label(message: str, label: str) -> int | float | None:
    variants = {
        label,
        label.replace("_", " "),
        label.replace("_", ""),
    }
    for variant in variants:
        pattern = re.compile(rf"\b{re.escape(variant)}\b\s*(?:is|=|:|to|of)?\s*(\d+(?:\.\d+)?)", re.IGNORECASE)
        match = pattern.search(message)
        if match:
            value = match.group(1)
            return float(value) if "." in value else int(value)
    return None


def _extract_name_after_phrase(message: str, phrase: str) -> str | None:
    pattern = re.compile(
        rf"{phrase}\s+(.+?)(?:\s+with|\s+email|\s+phone|\s+company|\s+industry|\s+lead\s+source|\s+budget|\s+interest|\s+status|\s+city|,|$)",
        re.IGNORECASE,
    )
    match = pattern.search(message)
    if match:
        return match.group(1).strip(" .,'\"")
    return None


def _extract_person_name_for_create(message: str, entity: str) -> str | None:
    phrases = {
        "lead": (
            "create a lead for",
            "create lead for",
            "add a lead for",
            "add lead for",
            "new lead for",
            "insert a lead for",
        ),
        "ticket": (
            "create a support ticket for",
            "create support ticket for",
            "create a ticket for",
            "create ticket for",
            "add a ticket for",
            "add ticket for",
            "open a ticket for",
            "raise a ticket for",
        ),
    }

    for phrase in phrases.get(entity, ()):
        extracted = _extract_name_after_phrase(message, phrase)
        if extracted:
            return extracted
    return None


def _extract_value_from_variants(message: str, *variants: str) -> str | None:
    return _extract_named_field(message, *variants)


def _normalize_choice(value: str | None, mapping: dict[str, str]) -> str | None:
    if value in (None, ""):
        return None
    normalized = " ".join(str(value).split()).strip().lower()
    return mapping.get(normalized, str(value).strip())


def _extract_query_type(message: str) -> str | None:
    explicit = _extract_value_from_variants(message, "query_type", "query type", "issue type", "type")
    normalized_explicit = _normalize_choice(explicit, QUERY_TYPE_NORMALIZATION)
    if normalized_explicit:
        return normalized_explicit

    lowered = message.lower()
    for phrase, normalized in QUERY_TYPE_NORMALIZATION.items():
        if phrase in lowered:
            return normalized
    return None


def _extract_identifier(entity: str, message: str) -> dict:
    email = _extract_email(message)
    if entity == "lead":
        return {
            "lead_id": _extract_number_after_label(message, "lead_id") or _extract_number_after_label(message, "id"),
            "email": email,
            "customer_name": _extract_named_field(message, "customer_name", "name"),
            "company": _extract_named_field(message, "company"),
        }
    if entity == "ticket":
        return {
            "ticket_id": _extract_number_after_label(message, "ticket_id") or _extract_number_after_label(message, "id"),
            "email": email,
            "customer_name": _extract_named_field(message, "customer_name", "name"),
            "issue_summary": _extract_named_field(message, "issue_summary", "issue", "summary", "problem"),
        }
    return {
        "campaign_id": _extract_number_after_label(message, "campaign_id") or _extract_number_after_label(message, "id"),
        "campaign_name": _extract_named_field(message, "campaign_name", "name"),
    }


def _identifier_missing_text(entity: str) -> str:
    if entity == "lead":
        return "lead_id, email, name, or company"
    if entity == "ticket":
        return "ticket_id, email, name, or issue_summary"
    return "campaign_id or campaign_name"


def _has_identifier(identifier: dict) -> bool:
    return any(value not in (None, "", 0) for value in identifier.values())


def _handle_lead_creation(message: str) -> str:
    customer_name = (
        _extract_named_field(message, "customer_name", "name")
        or _extract_person_name_for_create(message, "lead")
    )
    email = _extract_email(message)
    phone = _extract_phone(message)
    company = _extract_named_field(message, "company")
    industry = _extract_named_field(message, "industry")
    lead_source = _extract_value_from_variants(message, "lead_source", "lead source", "source") or "Chatbot"
    budget = int(_extract_number_after_label(message, "budget") or 0)
    interest_level = _normalize_choice(
        _extract_value_from_variants(message, "interest_level", "interest level", "interest"),
        LEAD_INTEREST_LEVELS,
    ) or "Medium"
    status = _normalize_choice(_extract_named_field(message, "status"), LEAD_STATUSES) or "New"
    city = _extract_named_field(message, "city")

    missing = [label for label, value in (("name", customer_name), ("email", email), ("company", company), ("industry", industry)) if not value]
    if missing:
        return (
            f"I can add the lead, but I still need: {', '.join(missing)}. "
            "Use a message like: create a lead name=Ryan Jain, email=ryan@example.com, company=OpenAI Test Co, industry=Technology."
        )

    lead = crm_service.create_lead(
        {
            "customer_name": customer_name,
            "email": email,
            "phone": phone,
            "company": company,
            "industry": industry,
            "lead_source": lead_source,
            "budget": budget,
            "interest_level": interest_level,
            "status": status,
            "city": city,
        }
    )
    return f"Lead created successfully for {lead['customer_name']} at {lead['company']}. Lead ID is {lead['lead_id']} and status is {lead['status']}."


def _handle_ticket_creation(message: str) -> str:
    customer_name = (
        _extract_named_field(message, "customer_name", "name")
        or _extract_person_name_for_create(message, "ticket")
    )
    email = _extract_email(message)
    query_type = _extract_query_type(message)
    issue_summary = _extract_value_from_variants(message, "issue_summary", "issue summary", "issue", "summary", "problem")
    product = _extract_named_field(message, "product")
    priority = _normalize_choice(_extract_named_field(message, "priority"), TICKET_PRIORITIES) or "Medium"
    status = _normalize_choice(_extract_named_field(message, "status"), TICKET_STATUSES) or "Open"
    assigned_department = _extract_value_from_variants(message, "assigned_department", "assigned department", "department") or "Support"
    response_time_hours = int(_extract_number_after_label(message, "response_time_hours") or 0)
    satisfaction_score = int(_extract_number_after_label(message, "satisfaction_score") or 3)

    missing = [label for label, value in (("name", customer_name), ("email", email), ("query type", query_type), ("issue summary", issue_summary), ("product", product)) if not value]
    if missing:
        return (
            f"I can create the support ticket, but I still need: {', '.join(missing)}. "
            "Use a message like: create a support ticket name=Ryan Jain, email=ryan@example.com, query_type=Technical Support, issue=Login issue, product=CRM Suite."
        )

    ticket = crm_service.create_support_ticket(
        {
            "customer_name": customer_name,
            "email": email,
            "query_type": query_type,
            "issue_summary": issue_summary,
            "product": product,
            "priority": priority,
            "status": status,
            "assigned_department": assigned_department,
            "response_time_hours": response_time_hours,
            "satisfaction_score": satisfaction_score,
        }
    )
    return f"Support ticket created for {ticket['customer_name']}. Ticket ID is {ticket['ticket_id']} with status {ticket['status']} in {ticket['assigned_department']}."


def _handle_campaign_creation(message: str) -> str:
    campaign_name = _extract_named_field(message, "campaign_name", "name")
    campaign_type = _normalize_choice(
        _extract_value_from_variants(message, "campaign_type", "campaign type", "type"),
        CAMPAIGN_TYPE_NORMALIZATION,
    )
    target_industry = _extract_value_from_variants(message, "target_industry", "target industry", "industry")
    budget = int(_extract_number_after_label(message, "budget") or 0)
    clicks = int(_extract_number_after_label(message, "clicks") or 0)
    impressions = int(_extract_number_after_label(message, "impressions") or 0)
    conversions = int(_extract_number_after_label(message, "conversions") or 0)
    conversion_rate = float(_extract_number_after_label(message, "conversion_rate") or 0.0)
    status = _normalize_choice(_extract_named_field(message, "status"), CAMPAIGN_STATUSES) or "Active"

    missing = [label for label, value in (("campaign name", campaign_name), ("campaign type", campaign_type), ("target industry", target_industry)) if not value]
    if missing:
        return (
            f"I can create the campaign, but I still need: {', '.join(missing)}. "
            "Use a message like: create a campaign campaign_name=June Launch, campaign_type=Email Marketing, target_industry=Technology, budget=12000."
        )

    campaign = crm_service.create_campaign(
        {
            "campaign_name": campaign_name,
            "campaign_type": campaign_type,
            "target_industry": target_industry,
            "budget": budget,
            "clicks": clicks,
            "impressions": impressions,
            "conversions": conversions,
            "conversion_rate": conversion_rate,
            "status": status,
        }
    )
    return f"Campaign created successfully: {campaign['campaign_name']}. Campaign ID is {campaign['campaign_id']} and status is {campaign['status']}."


def _handle_lead_update(message: str) -> str:
    identifier = _extract_identifier("lead", message)
    if not _has_identifier(identifier):
        return f"I can update the lead, but I need one identifier: {_identifier_missing_text('lead')}."

    updates = {
        "customer_name": _extract_named_field(message, "customer_name", "name"),
        "phone": _extract_phone(message),
        "company": _extract_named_field(message, "company"),
        "industry": _extract_named_field(message, "industry"),
        "lead_source": _extract_value_from_variants(message, "lead_source", "lead source", "source"),
        "budget": _extract_number_after_label(message, "budget"),
        "interest_level": _normalize_choice(
            _extract_value_from_variants(message, "interest_level", "interest level", "interest"),
            LEAD_INTEREST_LEVELS,
        ),
        "status": _normalize_choice(_extract_named_field(message, "status"), LEAD_STATUSES),
        "city": _extract_named_field(message, "city"),
    }
    lead = crm_service.update_lead(identifier, updates)
    if lead is None:
        return "I could not find the lead to update."
    return f"Lead updated successfully for {lead['customer_name']}. Lead ID is {lead['lead_id']} and status is {lead['status']}."


def _handle_ticket_update(message: str) -> str:
    identifier = _extract_identifier("ticket", message)
    if not _has_identifier(identifier):
        return f"I can update the support ticket, but I need one identifier: {_identifier_missing_text('ticket')}."

    updates = {
        "customer_name": _extract_named_field(message, "customer_name", "name"),
        "query_type": _extract_query_type(message),
        "issue_summary": _extract_value_from_variants(message, "issue_summary", "issue summary", "issue", "summary", "problem"),
        "product": _extract_named_field(message, "product"),
        "priority": _normalize_choice(_extract_named_field(message, "priority"), TICKET_PRIORITIES),
        "status": _normalize_choice(_extract_named_field(message, "status"), TICKET_STATUSES),
        "assigned_department": _extract_value_from_variants(message, "assigned_department", "assigned department", "department"),
        "response_time_hours": _extract_number_after_label(message, "response_time_hours"),
        "satisfaction_score": _extract_number_after_label(message, "satisfaction_score"),
    }
    ticket = crm_service.update_support_ticket(identifier, updates)
    if ticket is None:
        return "I could not find the support ticket to update."
    return f"Support ticket updated successfully for {ticket['customer_name']}. Ticket ID is {ticket['ticket_id']} and status is {ticket['status']}."


def _handle_campaign_update(message: str) -> str:
    identifier = _extract_identifier("campaign", message)
    if not _has_identifier(identifier):
        return f"I can update the campaign, but I need one identifier: {_identifier_missing_text('campaign')}."

    updates = {
        "campaign_name": _extract_named_field(message, "campaign_name", "name"),
        "campaign_type": _normalize_choice(
            _extract_value_from_variants(message, "campaign_type", "campaign type", "type"),
            CAMPAIGN_TYPE_NORMALIZATION,
        ),
        "target_industry": _extract_value_from_variants(message, "target_industry", "target industry", "industry"),
        "budget": _extract_number_after_label(message, "budget"),
        "clicks": _extract_number_after_label(message, "clicks"),
        "impressions": _extract_number_after_label(message, "impressions"),
        "conversions": _extract_number_after_label(message, "conversions"),
        "conversion_rate": _extract_number_after_label(message, "conversion_rate"),
        "status": _normalize_choice(_extract_named_field(message, "status"), CAMPAIGN_STATUSES),
        "launch_date": _extract_value_from_variants(message, "launch_date", "launch date"),
    }
    campaign = crm_service.update_campaign(identifier, updates)
    if campaign is None:
        return "I could not find the campaign to update."
    return f"Campaign updated successfully: {campaign['campaign_name']}. Campaign ID is {campaign['campaign_id']} and status is {campaign['status']}."


def _handle_lead_delete(message: str) -> str:
    identifier = _extract_identifier("lead", message)
    if not _has_identifier(identifier):
        return f"I can delete the lead, but I need one identifier: {_identifier_missing_text('lead')}."
    lead = crm_service.delete_lead(identifier)
    if lead is None:
        return "I could not find the lead to delete."
    return f"Lead deleted successfully for {lead['customer_name']} with lead ID {lead['lead_id']}."


def _handle_ticket_delete(message: str) -> str:
    identifier = _extract_identifier("ticket", message)
    if not _has_identifier(identifier):
        return f"I can delete the support ticket, but I need one identifier: {_identifier_missing_text('ticket')}."
    ticket = crm_service.delete_support_ticket(identifier)
    if ticket is None:
        return "I could not find the support ticket to delete."
    return f"Support ticket deleted successfully for {ticket['customer_name']} with ticket ID {ticket['ticket_id']}."


def _handle_campaign_delete(message: str) -> str:
    identifier = _extract_identifier("campaign", message)
    if not _has_identifier(identifier):
        return f"I can delete the campaign, but I need one identifier: {_identifier_missing_text('campaign')}."
    campaign = crm_service.delete_campaign(identifier)
    if campaign is None:
        return "I could not find the campaign to delete."
    return f"Campaign deleted successfully: {campaign['campaign_name']} with campaign ID {campaign['campaign_id']}."
