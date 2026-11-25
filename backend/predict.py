from pathlib import Path
import joblib
import numpy as np
from train_model import train

MODEL_PATH = Path(__file__).parent / "model" / "loan_model.joblib"
EMPLOYMENT_CODES = {"salaried": 0, "self_employed": 1, "other": 2}

def load_model():
    if not MODEL_PATH.exists():
        train(MODEL_PATH)
    return joblib.load(MODEL_PATH)["model"]

def predict_eligibility(payload, model):
    employment_code = EMPLOYMENT_CODES.get(payload.get("employment_type", "salaried"))
    if employment_code is None:
        raise ValueError("Invalid employment type.")
    features = np.array([[
        payload["applicant_income"], payload["coapplicant_income"],
        payload["monthly_debt"], payload["loan_amount"], payload["loan_term"],
        payload["credit_history"], employment_code
    ]], dtype=float)
    probabilities = model.predict_proba(features)[0]
    class_index = int(np.argmax(probabilities))
    return ("Eligible" if class_index == 1 else "Not Eligible", float(probabilities[class_index]))