CREATE DATABASE IF NOT EXISTS loanwise;
USE loanwise;

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
);