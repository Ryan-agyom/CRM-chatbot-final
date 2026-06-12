from app.ml.lead_status_model import lead_status_model

def main()->None:
    payload = {
        "lead_source":"Google Ads",
        "budget":22000,
        "interest_level":"High",
        "industry":"Technology",
    }
    prediction = lead_status_model.predict(payload)
    print("Predicted Status: ",prediction.predicted_status)
    print("Confidence:",prediction.confidence)
    print("Probabilites:",prediction.probabilities)

if __name__ == "__main__":
    main()