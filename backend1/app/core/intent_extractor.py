from __future__ import annotations

import json
import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_ollama import OllamaLLM

load_dotenv(Path(__file__).resolve().parents[3] / ".env")
load_dotenv(Path(__file__).resolve().parents[2] / ".env", override=False)

OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3").strip()
OLLAMA_API_URL = os.getenv("OLLAMA_API_URL", "http://127.0.0.1:11434").strip()
OLLAMA_API_KEY = os.getenv("OLLAMA_API_KEY", "").strip()

INTENT_PROMPT = PromptTemplate(
    input_variables=["message"],
    template="""
You are an intent extraction assistant for a CRM chatbot.

Your job is to understand the user's message and return only valid JSON.

The user may write naturally, casually, indirectly, or without exact field names.
Infer the user's real goal from meaning.

Supported intents:
- crm_query
- lead_prediction
- ticket_prediction
- campaign_prediction
- lead_creation
- lead_update
- ticket_creation
- ticket_update
- campaign_creation
- campaign_update
- delete_request
- general_chat

Important rules:
- Return only valid JSON.
- Do not include markdown.
- Infer intent from meaning, not only exact keywords.
- If the user is asking for CRM data lookup, analytics, filtering, aggregates, counts, sums, averages, comparisons, grouped summaries, top/bottom values, or SQL-like business questions, use "crm_query".
- If the user is asking to predict lead outcome, use "lead_prediction".
- If the user is asking to predict ticket priority or response time, use "ticket_prediction".
- If the user is asking to predict campaign conversions or conversion rate, use "campaign_prediction".
- If the user is asking to create/update/delete CRM records, use the matching action intent.
- Use "general_chat" only if the message is not a CRM query, prediction request, or CRM action.
- If a field is not present, use null.

CRM query examples:
- "What is the average budget of leads in the retail industry?" -> crm_query
- "How many open support tickets do we have?" -> crm_query
- "Show the top 5 campaigns by conversion rate." -> crm_query

Campaign prediction examples:
- "Predict campaign performance for an email marketing campaign targeting retail with a budget of 15000 and 4200 clicks." -> campaign_prediction

Lead prediction examples:
- "Predict whether a lead from LinkedIn with 12000 budget and high interest in technology is likely qualified." -> lead_prediction

Ticket prediction examples:
- "Predict the ticket priority for a billing inquiry about invoice mismatch." -> ticket_prediction
- "Estimate the response time for a technical support case about login failure." -> ticket_prediction

Campaign extraction rules:
- If the user says "email marketing campaign", set campaign_type to "Email Marketing".
- If the user says "social media campaign", set campaign_type to "Social Media".
- If the user says "ppc campaign", set campaign_type to "PPC".
- If the user says "retail industry", set target_industry to "Retail".
- If the user says "technology industry", set target_industry to "Technology".
- If the user says "healthcare industry", set target_industry to "Healthcare".
- If the user says "finance industry", set target_industry to "Finance".
- Extract budget values from phrases like "budget of 15000", "with 15000 budget", or "budget is 15000".
- Extract clicks values from phrases like "4200 clicks", "with 4200 clicks", or "clicks are 4200".

Ticket extraction rules:
- If the user says "billing inquiry", set query_type to "Billing Inquiry".
- If the user says "technical support", set query_type to "Technical Support".
- If the user says "refund request", set query_type to "Refund Request".
- If the user says "product inquiry", set query_type to "Product Inquiry".
- If the user says "feature request", set query_type to "Feature Request".
- If the user says "order delay", set query_type to "Order Delay".
- If the user says "account access", set query_type to "Account Access".
- Extract issue_summary from the problem description.
- Extract product from phrases like "product is CRM Suite".
- Extract assigned_department from phrases like "assigned department is Billing".
- Normalize query_type exactly to one of:
  Billing Inquiry
  Technical Support
  Refund Request
  Product Inquiry
  Feature Request
  Order Delay
  Account Access

Lead extraction rules:
- Extract lead_source, budget, interest_level, and industry when present.

Return JSON in this exact shape:
{{
  "intent": "crm_query|lead_prediction|ticket_prediction|campaign_prediction|lead_creation|lead_update|ticket_creation|ticket_update|campaign_creation|campaign_update|delete_request|general_chat",
  "lead_source": null,
  "budget": null,
  "interest_level": null,
  "industry": null,
  "query_type": null,
  "issue_summary": null,
  "product": null,
  "assigned_department": null,
  "customer_name": null,
  "company": null,
  "campaign_name": null,
  "campaign_type": null,
  "target_industry": null,
  "clicks": null
}}

User message:
{message}
""".strip(),
)


@lru_cache(maxsize=1)
def _create_llm() -> OllamaLLM:
    return OllamaLLM(
        model=OLLAMA_MODEL,
        base_url=OLLAMA_API_URL,
        api_key=OLLAMA_API_KEY or None,
        temperature=0,
    )


def extract_intent(message: str) -> dict:
    llm = _create_llm()
    prompt = INTENT_PROMPT.format(message=message)
    raw = llm.invoke(prompt)

    text = str(raw).strip()
    start = text.find("{")
    end = text.rfind("}")

    if start == -1 or end == -1:
        raise ValueError(f"Extractor did not return valid JSON: {text}")

    parsed = json.loads(text[start:end + 1])

    return {
        "intent": parsed.get("intent", "general_chat"),
        "lead_source": parsed.get("lead_source"),
        "budget": parsed.get("budget"),
        "interest_level": parsed.get("interest_level"),
        "industry": parsed.get("industry"),
        "query_type": parsed.get("query_type"),
        "issue_summary": parsed.get("issue_summary"),
        "product": parsed.get("product"),
        "assigned_department": parsed.get("assigned_department"),
        "customer_name": parsed.get("customer_name"),
        "company": parsed.get("company"),
        "campaign_name": parsed.get("campaign_name"),
        "campaign_type": parsed.get("campaign_type"),
        "target_industry": parsed.get("target_industry"),
        "clicks": parsed.get("clicks"),
    }