# FinSight API 📈🤖

FinSight is a B2B RESTful API designed for automated financial portfolio analysis. It leverages asynchronous processing to ingest real-time market data and implements a RAG (Retrieval-Augmented Generation) pipeline using AI to generate executive insights with zero risk of hallucinations.

## 🚀 Architecture & Tech Stack

The project is built on a containerized microservices architecture:

- **Backend Framework:** Django & Django REST Framework (DRF)
- **Database:** PostgreSQL (Multi-tenant data isolation)
- **Message Broker & Task Queue:** Redis + Celery (Asynchronous processing)
- **AI / LLM:** OpenAI API (GPT-4o-mini)
- **Data Source:** Yahoo Finance API (`yfinance`)
- **Infrastructure:** Docker & Docker Compose

## 🧠 Core Features

1. **Asynchronous Decoupling:** The API is strictly non-blocking. Heavy analysis requests immediately return an `HTTP 202 Accepted`, delegating AI computation and data ingestion to Celery workers via Redis.
2. **Retrieval-Augmented Generation (RAG):** To prevent the LLM from hallucinating or fabricating macroeconomic factors, Celery workers inject real-time news headlines directly into the System Prompt. If empirical data is missing, the AI explicitly refuses to speculate.
3. **Security & Multi-tenancy:** Endpoints are secured using JSON Web Tokens (JWT). Row-Level Security is implemented at the QuerySet level, guaranteeing that each user (Tenant) has strictly isolated access to their own portfolios.

## 🛠️ Local Environment Setup

1. Clone the repository.
2. Create a `.env` file in the root directory with your environment variables:
   ```env
   OPENAI_API_KEY=sk-your-key-here```


Spin up the infrastructure using Docker:

Bash
docker compose up --build -d

Create a superuser to access the platform:

Bash
docker compose exec web python manage.py createsuperuser

🗺️ Roadmap
[x] Market data ingestion (yfinance).
[x] Asynchronous processing (Celery + Redis).
[x] LLM integration with Defensive Prompt Engineering (RAG).
[x] JWT Authentication & Multi-tenant Isolation.
[ ] Phase 4: Unit Testing coverage (Pytest).
[ ] Phase 5: CI/CD Pipeline via GitHub Actions (Linting & Testing).
[ ] Phase 6: Cloud Deployment readiness (AWS ECS / RDS).