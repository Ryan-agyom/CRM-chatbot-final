from __future__ import annotations

import os
import re
from functools import lru_cache
from pathlib import Path
from time import perf_counter

import pandas as pd
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_ollama import OllamaLLM
from sqlalchemy import create_engine, text

from app.core.data_loader import get_campaigns_df, get_leads_df, get_tickets_df


load_dotenv(Path(__file__).resolve().parents[3] / ".env")
load_dotenv(Path(__file__).resolve().parents[2] / ".env", override=False)

SQL_MODEL = os.getenv("OLLAMA_SQL_MODEL", "llama3.2:3b").strip()
OLLAMA_API_URL = os.getenv("OLLAMA_API_URL", "http://127.0.0.1:11434").strip()
OLLAMA_API_KEY = os.getenv("OLLAMA_API_KEY", "").strip()

SQL_PROMPT = PromptTemplate(
    input_variables=["input"],
    template="""
You convert CRM questions into SQL for DuckDB.

Database schema:
leads(lead_id, customer_name, email, phone, company, industry, lead_source, budget, interest_level, status, city, created_at)
campaigns(campaign_id, campaign_name, campaign_type, target_industry, budget, clicks, impressions, conversions, conversion_rate, status, launch_date)
tickets(ticket_id, customer_name, email, query_type, issue_summary, product, priority, status, assigned_department, response_time_hours, satisfaction_score, created_at)

Rules:
- Return exactly one SQL query.
- Only generate read-only SQL.
- Use DuckDB syntax.
- Use only the tables and columns listed above.
- Prefer explicit column selection over SELECT *.
- For text filters such as industry, status, city, lead_source, campaign_type, target_industry, query_type, product, and assigned_department, use case-insensitive matching with LOWER(column) = LOWER('value').
- Treat all words given by the user in the prompt in a case-insensitive manner.
- If the request asks for "open" status, treat it as status = 'Open' or status = 'open'.
- If the request cannot be answered from this schema, return UNABLE_TO_ANSWER.
- Do not include markdown, backticks, commentary, or labels like "SQLQuery:".

User request:
{input}
""".strip(),
)


def init_duckdb_engine():
    engine = create_engine("duckdb:///:memory:")
    with engine.connect() as connection:
        get_leads_df().to_sql("leads", connection, if_exists="replace", index=False)
        get_campaigns_df().to_sql("campaigns", connection, if_exists="replace", index=False)
        get_tickets_df().to_sql("tickets", connection, if_exists="replace", index=False)
    return engine


@lru_cache(maxsize=1)
def get_duckdb_engine():
    return init_duckdb_engine()


@lru_cache(maxsize=1)
def _create_llm() -> OllamaLLM:
    return OllamaLLM(
        model=SQL_MODEL,
        base_url=OLLAMA_API_URL,
        api_key=OLLAMA_API_KEY or None,
        temperature=0,
    )


def _normalize_llm_sql_output(raw_output: str) -> str:
    cleaned = raw_output.strip()
    cleaned = cleaned.replace("```sql", "").replace("```", "").strip()

    if cleaned == "UNABLE_TO_ANSWER":
        return cleaned

    match = re.search(r"(?is)\b(select|with)\b.*", cleaned)
    if match:
        cleaned = match.group(0).strip()

    cleaned = re.sub(r";+\s*$", "", cleaned)
    return cleaned


def _is_safe_readonly_query(sql_query: str) -> bool:
    normalized = sql_query.strip().lower()
    if not normalized:
        return False
    if not (normalized.startswith("select") or normalized.startswith("with")):
        return False

    blocked_terms = (
        "insert ",
        "update ",
        "delete ",
        "drop ",
        "alter ",
        "truncate ",
        "create ",
        "replace ",
        "merge ",
        "copy ",
        "attach ",
        "detach ",
    )
    return not any(term in normalized for term in blocked_terms)


def generate_sql_from_natural_language(message: str) -> str:
    llm = _create_llm()
    prompt = SQL_PROMPT.format(input=message)
    started = perf_counter()
    response = llm.invoke(prompt)
    normalized = _normalize_llm_sql_output(str(response))
    print(f"[timing] sql_generation_ms={(perf_counter() - started) * 1000:.2f}")

    if normalized == "UNABLE_TO_ANSWER":
        return normalized

    if not _is_safe_readonly_query(normalized):
        raise ValueError(f"Ollama did not return a safe read-only SQL query. Raw output: {response}")

    return normalized


def execute_sql_query(sql_query: str) -> pd.DataFrame:
    engine = get_duckdb_engine()
    started = perf_counter()
    with engine.connect() as connection:
        result = connection.execute(text(sql_query))
        rows = result.mappings().all()
    print(f"[timing] sql_execution_ms={(perf_counter() - started) * 1000:.2f}")
    return pd.DataFrame(rows)


def format_sql_result(frame: pd.DataFrame) -> str:
    if frame.empty:
        return "I could not find matching data for that query."

    display_frame = frame.copy().fillna("")
    max_rows = 25
    truncated = len(display_frame) > max_rows
    if truncated:
        display_frame = display_frame.head(max_rows)

    rendered = display_frame.to_string(index=False)
    if truncated:
        return f"{rendered}\n\nShowing first {max_rows} rows out of {len(frame)}."
    return rendered


sql_chain = True
sql_agent = sql_chain
