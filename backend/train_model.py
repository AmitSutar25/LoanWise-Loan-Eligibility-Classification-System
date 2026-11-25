"""Train a demonstration-only model on synthetic data.
This synthetic dataset is not representative of real lending outcomes.
"""
from pathlib import Path
import numpy as np
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score

FEATURES = ["applicant_income", "coapplicant_income", "monthly_debt",
            "loan_amount", "loan_term", "credit_history", "employment_type_code"]

def make_dataset(n=6000, seed=42):
    rng = np.random.default_rng(seed)
    applicant = rng.lognormal(10.7, 0.55, n).clip(8000, 300000)
    coapp = rng.lognormal(9.4, 0.9, n).clip(0, 200000)
    debt = rng.lognormal(8.4, 0.8, n).clip(0, 100000)
    amount = rng.lognormal(12.8, 0.65, n).clip(50000, 5000000)
    term = rng.choice([12, 36, 60, 120, 180, 240, 360], n)
    credit = rng.choice([0, 1], n, p=[0.22, 0.78])
    employment = rng.choice([0, 1, 2], n, p=[0.65, 0.28, 0.07])
    monthly_payment = amount * 0.0105 * (360 / term) ** 0.12
    dti = (debt + monthly_payment) / np.maximum(applicant + coapp, 1)
    # A synthetic label rule, deliberately simple and not a real underwriting policy.
    score = (0.9 * credit + 0.45 * (dti < 0.45) + 0.25 * (dti < 0.30)
             + 0.15 * (applicant + coapp > 40000) + 0.08 * (employment == 0)
             - 0.35 * (dti > 0.65) + rng.normal(0, 0.22, n))
    y = (score >= 1.12).astype(int)
    X = np.column_stack([applicant, coapp, debt, amount, term, credit, employment])
    return X, y

def train(output_path=None):
    X, y = make_dataset()
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    model = RandomForestClassifier(n_estimators=180, max_depth=10, min_samples_leaf=5,
                                   class_weight="balanced", random_state=42, n_jobs=-1)
    model.fit(X_train, y_train)
    pred = model.predict(X_test)
    print(classification_report(y_test, pred, target_names=["Not Eligible", "Eligible"]))
    print("Confusion matrix:\\n", confusion_matrix(y_test, pred))
    print("ROC AUC:", round(roc_auc_score(y_test, model.predict_proba(X_test)[:, 1]), 3))
    output = Path(output_path or Path(__file__).parent / "model" / "loan_model.joblib")
    output.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump({"model": model, "features": FEATURES}, output)
    print(f"Saved model to {output}")
    return output

if __name__ == "__main__":
    train()