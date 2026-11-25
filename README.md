# LoanWise — Loan Eligibility Classification

A portfolio/learning project demonstrating a three-tier web application with a synthetic-data machine-learning classifier, Flask API, MySQL, Docker Compose and AWS deployment components.

> **Important:** This is an educational demonstration only. It is not a lender, credit scoring product, financial advice, or a real loan approval system. The model is trained on synthetic data generated from an illustrative rule. Its predictions and scores must never be used to make real lending decisions. Do not submit real personal or financial data.

## Architecture

- **Presentation tier:** HTML, CSS, JavaScript served by Nginx.
- **Application tier:** Python Flask REST API and scikit-learn Random Forest.
- **Data tier:** MySQL locally; Amazon RDS MySQL for AWS deployment.
- **Containers:** Docker images for frontend and backend; Docker Compose for local orchestration.
- **AWS:** EC2, ECR, RDS, VPC, public Application Load Balancer, S3 (optional model/artifact storage), IAM and CloudWatch.

## Project structure

```text
frontend/       Static web UI and Nginx configuration
backend/        Flask API, ML training and inference code
database/       SQL schema
docker-compose.yml
.env.example
```

## Prerequisites

- Docker Desktop (Windows/macOS) or Docker Engine + Compose plugin (Linux)
- Git (optional)
- For AWS: AWS account, AWS CLI v2, an IAM deployment identity and an EC2 key pair

## Run locally (Windows PowerShell)

1. Extract the project ZIP and open PowerShell in the project folder.
2. Copy environment template:

   ```powershell
   Copy-Item .env.example .env
   notepad .env
   ```

3. Replace both example passwords with long, unique values. Never commit `.env`.
4. Build and start:

   ```powershell
   docker compose up --build -d
   docker compose ps
   ```

5. Open **http://localhost:8080**.
6. Submit sample values and review the result and application history.
7. Check logs:

   ```powershell
   docker compose logs -f backend
   docker compose logs -f frontend
   docker compose logs -f db
   ```

8. Stop the stack:

   ```powershell
   docker compose down
   ```

   Remove local database data only if you intentionally want to reset it:

   ```powershell
   docker compose down -v
   ```

The backend trains a reproducible demonstration model on first startup if no saved model is present. Training metrics are printed in backend logs.

## API endpoints

- `GET /api/health` — API health check
- `POST /api/predict` — validate application input, predict and store record
- `GET /api/applications` — return the latest 25 records

Example request body:

```json
{
  "applicant_name": "Demo Applicant",
  "email": "demo@example.com",
  "applicant_income": 50000,
  "coapplicant_income": 10000,
  "monthly_debt": 5000,
  "loan_amount": 500000,
  "loan_term": 180,
  "credit_history": 1,
  "employment_type": "salaried",
  "loan_purpose": "home"
}
```

## AWS deployment outline

### 1. Create AWS resources

Use a custom VPC spanning at least two Availability Zones for an ALB. Place the internet-facing ALB in public subnets. Place EC2 application instances in private subnets where practical, and RDS in private DB subnets. For a first low-cost learning deployment, a single EC2 in a public subnet can be used temporarily with strict inbound rules, but do not expose MySQL to the internet.

Suggested security group rules:
- ALB SG: inbound TCP 80 from `0.0.0.0/0` (and 443 after TLS setup).
- EC2 SG: inbound TCP 8080 from the ALB SG only; SSH 22 only from your current trusted IP if needed. Prefer Systems Manager Session Manager instead of public SSH.
- RDS SG: inbound TCP 3306 from the EC2 application SG only.
- Never open database port 3306 to `0.0.0.0/0`.

Create an RDS MySQL database in private subnets. Create an ECR repository for each image. Attach an EC2 IAM role with least-privilege ECR pull permissions and CloudWatch logging permissions. Store DB credentials in Secrets Manager or inject them securely at deployment time.

### 2. Build and push images to ECR

Create repositories named `loanwise-frontend` and `loanwise-backend`. Replace account ID and region below.

```bash
aws ecr get-login-password --region ap-south-1 | docker login --username AWS --password-stdin ACCOUNT_ID.dkr.ecr.ap-south-1.amazonaws.com

docker build -t loanwise-backend ./backend
docker tag loanwise-backend:latest ACCOUNT_ID.dkr.ecr.ap-south-1.amazonaws.com/loanwise-backend:latest
docker push ACCOUNT_ID.dkr.ecr.ap-south-1.amazonaws.com/loanwise-backend:latest

docker build -t loanwise-frontend ./frontend
docker tag loanwise-frontend:latest ACCOUNT_ID.dkr.ecr.ap-south-1.amazonaws.com/loanwise-frontend:latest
docker push ACCOUNT_ID.dkr.ecr.ap-south-1.amazonaws.com/loanwise-frontend:latest
```

### 3. Configure the EC2 host

Install Docker Engine and the Docker Compose plugin using the current official instructions for your chosen EC2 operating system. Attach an IAM role to EC2, then authenticate to ECR and pull both images.

Create a production Compose file on EC2 that uses the ECR image URIs, and remove the local `db` service. Set the backend `DATABASE_URL` to your RDS endpoint using a secret, for example:

```text
mysql+pymysql://DB_USER:URL_ENCODED_PASSWORD@RDS_ENDPOINT:3306/loanwise
```

The RDS database must exist and the application table must be initialized. You can create it using `database/schema.sql` or allow the backend's initialization routine to create it. For production, use a controlled schema migration process.

Publish only the Nginx frontend port on the EC2 host (for example `8080:80`). Do not publish backend port 5000 or database port 3306. Configure the ALB target group to forward to EC2 port 8080 and use `/` for its health check. Configure HTTPS with an ACM certificate before public production use.

### 4. Validate

```bash
docker compose ps
docker compose logs --tail=100 backend
curl http://localhost:8080/api/health
```

Browse to the ALB DNS name after its target is healthy.

## AWS cost and security notes

- AWS resources may incur charges even when idle. Review current regional pricing before creating EC2, RDS, ALB, NAT Gateway, EBS, S3 and CloudWatch resources.
- NAT Gateways and load balancers can be significant costs for a small practice project. Build locally first; create AWS resources only when ready and delete them after practice.
- Do not commit `.env`, database passwords, private keys or AWS credentials.
- Use HTTPS, least-privilege IAM, private database subnets, backups and log retention.
- The sample app has no user authentication, rate limiting, CSRF protection, formal privacy controls or production security review. Do not expose it as a real financial service.
- The local MySQL service is for development only. Use managed RDS with private networking for the AWS deployment.

## Learning enhancements

1. Add GitHub Actions to test, build and push images to ECR.
2. Deploy multiple EC2 instances behind an ALB and configure Auto Scaling.
3. Add HTTPS with ACM and a domain name.
4. Add CloudWatch dashboards, alarms and structured application logs.
5. Add authentication and audit controls before any real user-data use.
6. Replace synthetic training data with a properly licensed, documented dataset and conduct rigorous fairness, privacy and model-risk reviews before any consequential use.
