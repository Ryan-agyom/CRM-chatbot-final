from app.services.ticket_prediction_service import ticket_prediction_service


def main() -> None:
    payload = {
        "query_type": "Technical Support",
        "issue_summary": "Customer cannot log in to the CRM dashboard and password reset is not working.",
        "product": "CRM Suite",
        "assigned_department": "Technical",
    }

    result = ticket_prediction_service.predict(payload)
    print(result)


if __name__ == "__main__":
    main()