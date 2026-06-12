from pathlib import Path

from app.core.synthetic_crm_data import build_synthetic_dataset


DATA_DIR = Path(__file__).resolve().parents[1] / "data"


def main() -> None:
    dataset = build_synthetic_dataset(leads=500, campaigns=500, tickets=500)
    dataset["leads"].to_csv(DATA_DIR / "crm_leads.csv", index=False)
    dataset["campaigns"].to_csv(DATA_DIR / "crm_campaigns.csv", index=False)
    dataset["tickets"].to_csv(DATA_DIR / "crm_support_tickets.csv", index=False)
    print("Synthetic CRM CSV files generated successfully")


if __name__ == "__main__":
    main()
