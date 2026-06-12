from __future__ import annotations

from pathlib import Path
from datetime import date

import pandas as pd

from app.core.cache_utils import clear_backend_caches
from app.core.data_loader import (
    CAMPAIGNS_DTYPES,
    DATA_DIR,
    LEADS_DTYPES,
    TICKETS_DTYPES,
    get_campaigns_df,
    get_leads_df,
    get_tickets_df,
)


class CRMRepository:
    def __init__(self) -> None:
        self._data_dir = Path(DATA_DIR)

    def list_leads(self) -> list[dict]:
        frame = get_leads_df().copy()
        return self._serialize(frame)

    def list_campaigns(self) -> list[dict]:
        frame = get_campaigns_df().copy()
        return self._serialize(frame)

    def list_tickets(self) -> list[dict]:
        frame = get_tickets_df().copy()
        return self._serialize(frame)

    def create_lead(self, payload: dict) -> dict:
        frame = get_leads_df().copy()
        record = {
            "lead_id": int(frame["lead_id"].max()) + 1 if not frame.empty else 1,
            **payload,
            "created_at": date.today().isoformat(),
        }
        updated = self._append_record(frame, record)
        self._write_csv("crm_leads.csv", updated, LEADS_DTYPES, ["created_at"])
        return self._serialize(pd.DataFrame([record]))[0]

    def update_lead(self, identifier: dict, updates: dict) -> dict | None:
        return self._update_record(
            get_leads_df().copy(),
            "crm_leads.csv",
            LEADS_DTYPES,
            ["created_at"],
            identifier,
            updates,
        )

    def delete_lead(self, identifier: dict) -> dict | None:
        return self._delete_record(
            get_leads_df().copy(),
            "crm_leads.csv",
            LEADS_DTYPES,
            ["created_at"],
            identifier,
        )

    def create_campaign(self, payload: dict) -> dict:
        frame = get_campaigns_df().copy()
        record = {
            "campaign_id": int(frame["campaign_id"].max()) + 1 if not frame.empty else 1,
            **payload,
            "launch_date": payload.get("launch_date") or date.today().isoformat(),
        }
        updated = self._append_record(frame, record)
        self._write_csv("crm_campaigns.csv", updated, CAMPAIGNS_DTYPES, ["launch_date"])
        return self._serialize(pd.DataFrame([record]))[0]

    def update_campaign(self, identifier: dict, updates: dict) -> dict | None:
        return self._update_record(
            get_campaigns_df().copy(),
            "crm_campaigns.csv",
            CAMPAIGNS_DTYPES,
            ["launch_date"],
            identifier,
            updates,
        )

    def delete_campaign(self, identifier: dict) -> dict | None:
        return self._delete_record(
            get_campaigns_df().copy(),
            "crm_campaigns.csv",
            CAMPAIGNS_DTYPES,
            ["launch_date"],
            identifier,
        )

    def create_ticket(self, payload: dict) -> dict:
        frame = get_tickets_df().copy()
        record = {
            "ticket_id": int(frame["ticket_id"].max()) + 1 if not frame.empty else 1,
            **payload,
            "created_at": date.today().isoformat(),
        }
        updated = self._append_record(frame, record)
        self._write_csv("crm_support_tickets.csv", updated, TICKETS_DTYPES, ["created_at"])
        return self._serialize(pd.DataFrame([record]))[0]

    def update_ticket(self, identifier: dict, updates: dict) -> dict | None:
        return self._update_record(
            get_tickets_df().copy(),
            "crm_support_tickets.csv",
            TICKETS_DTYPES,
            ["created_at"],
            identifier,
            updates,
        )

    def delete_ticket(self, identifier: dict) -> dict | None:
        return self._delete_record(
            get_tickets_df().copy(),
            "crm_support_tickets.csv",
            TICKETS_DTYPES,
            ["created_at"],
            identifier,
        )

    def replace_all(self, *, leads: pd.DataFrame, campaigns: pd.DataFrame, tickets: pd.DataFrame) -> dict:
        self._write_csv("crm_leads.csv", leads, LEADS_DTYPES, ["created_at"])
        self._write_csv("crm_campaigns.csv", campaigns, CAMPAIGNS_DTYPES, ["launch_date"])
        self._write_csv("crm_support_tickets.csv", tickets, TICKETS_DTYPES, ["created_at"])
        return {
            "leads": len(leads),
            "campaigns": len(campaigns),
            "tickets": len(tickets),
        }

    def snapshot(self) -> dict[str, list[dict]]:
        return {
            "leads": self.list_leads(),
            "campaigns": self.list_campaigns(),
            "tickets": self.list_tickets(),
        }

    def _write_csv(
        self,
        filename: str,
        frame: pd.DataFrame,
        dtypes: dict[str, str],
        date_columns: list[str],
    ) -> None:
        normalized = frame.copy()
        for column in date_columns:
            normalized.loc[:, column] = pd.to_datetime(normalized[column]).dt.strftime("%Y-%m-%d").astype("string")
        ordered_columns = list(dtypes.keys()) + date_columns
        normalized = normalized[ordered_columns]
        normalized.to_csv(self._data_dir / filename, index=False)
        clear_backend_caches()

    @staticmethod
    def _serialize(frame: pd.DataFrame) -> list[dict]:
        serialized = frame.copy()
        for column in serialized.columns:
            if column.endswith("_at") or column.endswith("_date"):
                parsed = pd.to_datetime(serialized[column], errors="coerce")
                if parsed.notna().any():
                    serialized = serialized.astype({column: "object"})
                    serialized.loc[:, column] = parsed.dt.strftime("%Y-%m-%d").fillna(serialized[column])
        return serialized.to_dict(orient="records")

    @staticmethod
    def _append_record(frame: pd.DataFrame, record: dict) -> pd.DataFrame:
        row = {column: record.get(column) for column in frame.columns}
        if frame.empty:
            return pd.DataFrame([row], columns=frame.columns)
        return pd.concat([frame, pd.DataFrame([row], columns=frame.columns)], ignore_index=True)

    def _update_record(
        self,
        frame: pd.DataFrame,
        filename: str,
        dtypes: dict[str, str],
        date_columns: list[str],
        identifier: dict,
        updates: dict,
    ) -> dict | None:
        index = self._find_record_index(frame, identifier)
        if index is None:
            return None

        update_payload = {key: value for key, value in updates.items() if key in frame.columns and value is not None}
        if not update_payload:
            return self._serialize(frame.iloc[[index]].copy())[0]

        for key, value in update_payload.items():
            frame.loc[index, key] = value

        self._write_csv(filename, frame, dtypes, date_columns)
        refreshed = self._reload_by_filename(filename)
        refreshed_index = self._find_record_index(refreshed, identifier)
        if refreshed_index is None:
            return None
        return self._serialize(refreshed.iloc[[refreshed_index]].copy())[0]

    def _delete_record(
        self,
        frame: pd.DataFrame,
        filename: str,
        dtypes: dict[str, str],
        date_columns: list[str],
        identifier: dict,
    ) -> dict | None:
        index = self._find_record_index(frame, identifier)
        if index is None:
            return None

        deleted = self._serialize(frame.iloc[[index]].copy())[0]
        remaining = frame.drop(index=index).reset_index(drop=True)
        self._write_csv(filename, remaining, dtypes, date_columns)
        return deleted

    @staticmethod
    def _find_record_index(frame: pd.DataFrame, identifier: dict) -> int | None:
        for key, value in identifier.items():
            if key not in frame.columns or value is None:
                continue
            matches = frame.index[frame[key].astype(str).str.lower() == str(value).lower()].tolist()
            if matches:
                return matches[0]
        return None

    @staticmethod
    def _reload_by_filename(filename: str) -> pd.DataFrame:
        if filename == "crm_leads.csv":
            return get_leads_df().copy()
        if filename == "crm_campaigns.csv":
            return get_campaigns_df().copy()
        return get_tickets_df().copy()


crm_repository = CRMRepository()
