# url_service (URL Shortener Microservice)

[![Python Version](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111.0-009688.svg)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL%2016-336791.svg)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Deployment-Docker-blue.svg)](https://www.docker.com/)
[![Kubernetes](https://img.shields.io/badge/Orchestration-Kubernetes-326CE5.svg)](https://kubernetes.io/)

## 📝 Project Description

**`url_service`** is a modernized, highly-scalable, production-grade URL Shortener microservice. It is designed to be completely stateless, relying on API Gateway authentication injection (`X-User-Id`) and PostgreSQL for data persistence.

Built with **FastAPI** and **SQLAlchemy 2.0 (Async)**, the application natively integrates with enterprise deployment practices, utilizing container-native secret volumes, automated Alembic migrations, and structured `structlog` JSON correlation logging.

---

## ✨ Key Features

- **🔗 Core URL Management:** Auto-generate secure 6-character short URLs, create custom aliases, update metadata, and seamlessly redirect traffic. Includes soft-delete functionality to preserve analytical integrity.
- **🛡️ Stateless Header Authentication:** Drops bulky JWT decoding layers. Relies entirely on trust-based HTTP header injection (`X-User-Id`) provided by an external API Gateway or Auth Proxy.
- **🔐 Volume-Mounted Secrets:** Cloud-native secrets loading strategy mapping runtime environment configuration dynamically from a mounted `/secrets` volume.
- **📊 Observability & Logging:** Built-in Prometheus metrics instrumentation (`/metrics`) and comprehensive request tracing using structured, unified JSON logging (`structlog`).
- **🗃️ Async PostgreSQL + Alembic:** High-performance async driver (`asyncpg`/`aiosqlite`) coupled with Docker-native automated database migrations.
- **🧪 Comprehensive Test Suite:** 26 automated unit, integration, and E2E Pytest fixtures leveraging in-memory SQLite for lightning-fast CI/CD runs.

---

## ⚙️ Quick Start

The recommended way to run this microservice locally is using Docker Compose.

### Docker Compose Setup

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/SkeyRahaman/URL_Shortner
   cd URL_Shortner
   ```

2. **Spin Up the Stack:**
   This will build the API image, inject the mock development secrets, spin up a PostgreSQL 16 container, and automatically execute Alembic migrations on startup.
   ```bash
   docker-compose up --build -d
   ```

3. **Verify:**
   - **Base API Address:** `http://localhost:8080`
   - **Swagger Interactive Docs:** `http://localhost:8080/docs`
   - **Health Check:** `http://localhost:8080/health`
   - **Metrics:** `http://localhost:8080/metrics`

### Local Virtual Environment (Testing)

To run the automated test suite locally:
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Run all tests using local SQLite
pytest tests/
```

---

## 🗃️ Secrets Management

Configuration relies on injecting files into a specific directory (`/secrets` in Docker, `./secrets` locally).
For a local `NON_PROD` environment, you will find files such as:
- `secrets/NON_PROD_DATABASE_NAME` -> `url_service`
- `secrets/NON_PROD_DATABASE_HOSTNAME` -> `database`

This structure seamlessly bridges the gap between Docker Compose and Kubernetes Secret Volumes.

---

## 📚 API Endpoints

All endpoints use `application/json`.
Endpoints interacting with short URLs (except redirects/metadata) **require** the `X-User-Id` HTTP header.

| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :---: |
| `POST` | `/links` | Create a short URL (Auto or Custom Slug) | `X-User-Id` Header |
| `GET` | `/links` | List paginated short URLs owned by the user | `X-User-Id` Header |
| `GET` | `/links/{slug}` | Redirect to original long URL | No |
| `GET` | `/links/{slug}/details` | Get short URL metadata | No |
| `PUT` | `/links/{slug}` | Update short URL destination or description | `X-User-Id` Header |
| `PATCH`| `/links/{slug}/deactivate` | Temporarily deactivate a short URL | `X-User-Id` Header |
| `DELETE` | `/links/{slug}` | Soft Delete a short URL | `X-User-Id` Header |
| `GET` | `/health` | Check API server health status | No |
| `GET` | `/metrics` | Prometheus metrics exporter | No |

---

## 🚀 Deployment (Kubernetes)

Deployment manifests are deferred to a follow-up implementation.

---

## 🤝 Contributing Guidelines

1. **Fork** the repository.
2. **Create a feature branch:** `git checkout -b feature/your-feature-name`.
3. **Commit your changes** with clear messages.
4. **Run tests** to verify zero regressions (`pytest`).
5. **Open a Pull Request** to the `main` branch.

---

## 📞 Contact / Support

- **GitHub Profile:** [SkeyRahaman](https://github.com/SkeyRahaman/URL_Shortner)
- **Email:** [sakibmondal7@gmail.com](mailto:sakibmondal7@gmail.com)
- **Issues:** [GitHub Issues Page](https://github.com/SkeyRahaman/URL_Shortner/issues)