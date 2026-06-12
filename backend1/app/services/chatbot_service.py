from __future__ import annotations

from app.core.ai_provider import generate_reply
from app.core.chat_actions import try_handle_chat_action
from app.core.intent_extractor import extract_intent
from app.core.langchain_sql_chain import (
    execute_sql_query,
    format_sql_result,
    generate_sql_from_natural_language,
)
from app.core.memory import remember
from app.core.prompts import build_prompt
from app.core.sessions import append_message, get_history
from app.services.lead_prediction_service import lead_prediction_service
from app.services.ticket_prediction_service import ticket_prediction_service
from app.services.campaign_prediction_service import campaign_prediction_service


async def _process_crm_question_with_sql(message: str) -> str:
    try:
        sql_query = generate_sql_from_natural_language(message)
        if sql_query == "UNABLE_TO_ANSWER":
            return "I could not translate that request into a CRM SQL query."

        result = execute_sql_query(sql_query)
        return format_sql_result(result)
    except Exception as e:
        return f"I encountered an issue processing your CRM query: {str(e)}"


async def _handle_lead_prediction(extracted: dict) -> str:
    missing = [
        field
        for field in ("lead_source", "budget", "interest_level", "industry")
        if extracted.get(field) in (None, "")
    ]

    if missing:
        return (
            f"I can predict the lead outcome, but I still need: {', '.join(missing)}. "
            "Please provide the missing details."
        )

    prediction = lead_prediction_service.predict(extracted)

    return (
        f"This lead is likely {prediction['predicted_status']}. "
        f"Confidence: {prediction['confidence']:.2f}. "
        f"Probabilities: {prediction['probabilities']}."
    )


async def _handle_ticket_prediction(extracted: dict) -> str:
    missing = [
        field
        for field in ("query_type", "issue_summary", "product", "assigned_department")
        if extracted.get(field) in (None, "")
    ]

    if missing:
        return (
            f"I can predict the support ticket outcome, but I still need: {', '.join(missing)}. "
            "Please provide the missing details."
        )

    prediction = ticket_prediction_service.predict(extracted)

    return (
        f"Predicted priority: {prediction['predicted_priority']}. "
        f"Priority confidence: {prediction['priority_confidence']:.2f}. "
        f"Expected response time: {prediction['predicted_response_time_hours']:.2f} hours. "
        f"Priority probabilities: {prediction['priority_probabilities']}."
    )


async def _handle_mutation(message: str) -> str:
    try:
        action_reply = try_handle_chat_action(message)
        if action_reply:
            return action_reply
    except Exception as e:
        return f"I understood this as a CRM action request, but I hit an error while processing it: {str(e)}"

    return (
        "I understood this as a CRM action request, but I could not safely parse all required details. "
        "Please provide the record details more clearly."
    )


async def process_chat(message, session_id):
    history = get_history(session_id)

    try:
        extracted = extract_intent(message)
    except Exception:
        extracted = {"intent": "general_chat"}

    intent = extracted.get("intent", "general_chat")
    if intent == "campaign_prediction":
        reply = await _handle_campaign_prediction(extracted)
        append_message(session_id, "user", message)
        append_message(session_id, "assistant", reply)
        remember(session_id, {"last_module": "crm", "last_action": "campaign_prediction"})
        return {"sessionId": session_id, "reply": reply}
    if intent == "ticket_prediction":
        reply = await _handle_ticket_prediction(extracted)
        append_message(session_id, "user", message)
        append_message(session_id, "assistant", reply)
        remember(session_id, {"last_module": "crm", "last_action": "ticket_prediction"})
        return {"sessionId": session_id, "reply": reply}

    if intent == "lead_prediction":
        reply = await _handle_lead_prediction(extracted)
        append_message(session_id, "user", message)
        append_message(session_id, "assistant", reply)
        remember(session_id, {"last_module": "crm", "last_action": "lead_prediction"})
        return {"sessionId": session_id, "reply": reply}

    if intent == "crm_query":
        reply = await _process_crm_question_with_sql(message)
        append_message(session_id, "user", message)
        append_message(session_id, "assistant", reply)
        remember(session_id, {"last_module": "crm", "last_action": "query"})
        return {"sessionId": session_id, "reply": reply}

    if intent in {
        "lead_creation",
        "lead_update",
        "ticket_creation",
        "ticket_update",
        "campaign_creation",
        "campaign_update",
        "delete_request",
    }:
        reply = await _handle_mutation(message)
        append_message(session_id, "user", message)
        append_message(session_id, "assistant", reply)
        remember(session_id, {"last_module": "crm", "last_action": "mutation"})
        return {"sessionId": session_id, "reply": reply}

    prompt = build_prompt(message=message, history=history, module="general")
    reply = await generate_reply(prompt)
    append_message(session_id, "user", message)
    append_message(session_id, "assistant", reply)
    remember(session_id, {"last_module": "general"})
    return {"sessionId": session_id, "reply": reply}

async def _handle_campaign_prediction(extracted: dict) -> str:
    missing = [
        field
        for field in ("campaign_type", "target_industry", "budget", "clicks")
        if extracted.get(field) in (None, "")
    ]

    if missing:
        return (
            f"I can predict the campaign outcome, but I still need: {', '.join(missing)}. "
            "Please provide the missing details."
        )

    prediction = campaign_prediction_service.predict(extracted)

    return (
        f"Predicted conversions: {prediction['predicted_conversions']}. "
        f"Predicted conversion rate: {prediction['predicted_conversion_rate']}."
    )
