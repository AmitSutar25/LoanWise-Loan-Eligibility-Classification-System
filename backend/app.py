import os
from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS
from sqlalchemy.exc import SQLAlchemyError
from database import initialize_database, save_application, get_applications
from predict import load_model, predict_eligibility

app = Flask(__name__)
CORS(app)
model = load_model()

@app.get("/api/health")
def health():
    return jsonify(status="ok", service="loanwise-api", timestamp=datetime.utcnow().isoformat() + "Z")

@app.post("/api/predict")
def predict():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify(error="Expected a JSON request body."), 400
    required = ["applicant_name", "email", "applicant_income", "coapplicant_income",
                "monthly_debt", "loan_amount", "loan_term", "credit_history",
                "employment_type", "loan_purpose"]
    missing = [field for field in required if field not in data or data[field] in (None, "")]
    if missing:
        return jsonify(error="Missing required fields: " + ", ".join(missing)), 400
    try:
        clean = {
            "applicant_name": str(data["applicant_name"]).strip(),
            "email": str(data["email"]).strip(),
            "applicant_income": float(data["applicant_income"]),
            "coapplicant_income": float(data["coapplicant_income"]),
            "monthly_debt": float(data["monthly_debt"]),
            "loan_amount": float(data["loan_amount"]),
            "loan_term": int(data["loan_term"]),
            "credit_history": int(data["credit_history"]),
            "employment_type": str(data["employment_type"]),
            "loan_purpose": str(data["loan_purpose"])
        }
        if not clean["applicant_name"] or len(clean["applicant_name"]) > 100:
            raise ValueError("Applicant name must be between 1 and 100 characters.")
        if "@" not in clean["email"] or len(clean["email"]) > 150:
            raise ValueError("Enter a valid email address.")
        numeric = ["applicant_income", "coapplicant_income", "monthly_debt", "loan_amount"]
        if any(clean[k] < 0 for k in numeric) or clean["loan_amount"] <= 0:
            raise ValueError("Income and debt cannot be negative; loan amount must be positive.")
        if clean["loan_term"] not in [12, 36, 60, 120, 180, 240, 360]:
            raise ValueError("Unsupported loan term.")
        if clean["credit_history"] not in [0, 1]:
            raise ValueError("Invalid credit history value.")
        if clean["employment_type"] not in ["salaried", "self_employed", "other"]:
            raise ValueError("Invalid employment type.")
        if clean["loan_purpose"] not in ["home", "education", "vehicle", "personal", "business"]:
            raise ValueError("Invalid loan purpose.")
        prediction, score = predict_eligibility(clean, model)
        application_id = save_application(clean, prediction, score)
        return jsonify(application_id=application_id, prediction=prediction,
                       model_score=round(score, 6), loan_amount=clean["loan_amount"]), 201
    except (ValueError, TypeError) as exc:
        return jsonify(error=str(exc)), 400
    except SQLAlchemyError:
        app.logger.exception("Database operation failed")
        return jsonify(error="Database is unavailable. Check the database configuration."), 503

@app.get("/api/applications")
def applications():
    try:
        rows = get_applications()
        for row in rows:
            row["loan_amount"] = float(row["loan_amount"])
            row["model_score"] = float(row["model_score"])
            row["created_at"] = row["created_at"].isoformat() if row["created_at"] else None
        return jsonify(applications=rows)
    except SQLAlchemyError:
        app.logger.exception("Could not retrieve applications")
        return jsonify(error="Database is unavailable."), 503

if __name__ == "__main__":
    initialize_database()
    app.run(host="0.0.0.0", port=5000, debug=False)