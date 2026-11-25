
import os
from sqlalchemy import create_engine, text

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:////tmp/loanwise.db"
)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=280
)


def initialize_database():

    with engine.begin() as conn:

        if not DATABASE_URL.startswith("sqlite"):

            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS applications (
                    id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                    applicant_name VARCHAR(100) NOT NULL,
                    email VARCHAR(150) NOT NULL,
                    applicant_income DECIMAL(14,2) NOT NULL,
                    coapplicant_income DECIMAL(14,2) NOT NULL,
                    monthly_debt DECIMAL(14,2) NOT NULL,
                    loan_amount DECIMAL(14,2) NOT NULL,
                    loan_term INT NOT NULL,
                    credit_history TINYINT NOT NULL,
                    employment_type VARCHAR(30) NOT NULL,
                    loan_purpose VARCHAR(30) NOT NULL,
                    prediction VARCHAR(30) NOT NULL,
                    model_score DECIMAL(7,6) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))

        else:

            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS applications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    applicant_name TEXT NOT NULL,
                    email TEXT NOT NULL,
                    applicant_income REAL NOT NULL,
                    coapplicant_income REAL NOT NULL,
                    monthly_debt REAL NOT NULL,
                    loan_amount REAL NOT NULL,
                    loan_term INTEGER NOT NULL,
                    credit_history INTEGER NOT NULL,
                    employment_type TEXT NOT NULL,
                    loan_purpose TEXT NOT NULL,
                    prediction TEXT NOT NULL,
                    model_score REAL NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))


def save_application(data, prediction, score):

    with engine.begin() as conn:

        result = conn.execute(text("""
            INSERT INTO applications
            (
                applicant_name,
                email,
                applicant_income,
                coapplicant_income,
                monthly_debt,
                loan_amount,
                loan_term,
                credit_history,
                employment_type,
                loan_purpose,
                prediction,
                model_score
            )
            VALUES (
                :applicant_name,
                :email,
                :applicant_income,
                :coapplicant_income,
                :monthly_debt,
                :loan_amount,
                :loan_term,
                :credit_history,
                :employment_type,
                :loan_purpose,
                :prediction,
                :model_score
            )
        """), {
            **data,
            "prediction": prediction,
            "model_score": score
        })

        return result.lastrowid


def get_applications(limit=25):

    with engine.connect() as conn:

        rows = conn.execute(text("""
            SELECT
                id,
                applicant_name,
                loan_amount,
                prediction,
                model_score,
                created_at
            FROM applications
            ORDER BY id DESC
            LIMIT :limit
        """), {
            "limit": limit
        }).mappings().all()

    return [dict(row) for row in rows]
