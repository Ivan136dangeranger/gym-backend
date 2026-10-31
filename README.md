
# Gym Backend API

A REST API for managing fitness club clients, trainers, and subscriptions, built with Python, Django REST Framework, and PostgreSQL.

This portfolio project demonstrates backend API development, database transactions, access control, background task processing, automated testing, and application monitoring.

## Tech Stack

| Area | Technologies |
| --- | --- |
| Backend | Python 3.13, Django, Django REST Framework |
| Database | PostgreSQL 17, Django ORM |
| Authentication | JWT (Simple JWT) |
| Caching | Redis |
| Background tasks | Celery, RabbitMQ |
| Containers | Docker, Docker Compose |
| Testing | pytest, pytest-django |
| Monitoring | Prometheus, Grafana, Sentry |

## Features

- REST API endpoints for clients and subscriptions.
- Client–trainer relationships.
- JWT authentication and access restrictions based on user roles and ownership.
- Filtering, pagination, and data validation.
- Subscription session tracking, including checks for inactive subscriptions and insufficient remaining sessions.
- Protection against concurrent session deductions.
- Redis integration for caching.
- Asynchronous demo notification tasks with Celery and RabbitMQ.
- Application metrics and monitoring with Prometheus, Grafana, and Sentry.
- Automated API, transaction, and concurrency tests.

## Subscription Business Logic

Subscription session usage is handled by a dedicated service function. It uses:

- `transaction.atomic()` to group database operations into a transaction.
- `select_for_update()` to lock the subscription row during the transaction.
- Django `F()` expressions to decrement the remaining-session count in the database.
- Validation to reject inactive subscriptions or subscriptions with no remaining sessions.

These measures help prevent race conditions when multiple requests attempt to use the same subscription simultaneously.

## Background Tasks

The application uses **Celery** workers with **RabbitMQ** as a message broker.

When a subscription is created and the client has an email address, the application schedules a notification task using `transaction.on_commit()`. This prevents the task from being queued before the database transaction successfully commits.

> **Current limitation:** The email task is a demonstration only. It simulates work and returns a message; it does **not** send an actual email.

## Testing

Automated tests cover:

- Client and subscription API operations.
- Input validation and business rules.
- Subscription usage and error cases.
- Notification scheduling after a successful transaction and suppression after rollback.
- Concurrent subscription session usage.

**Latest recorded local test run:** 28 tests passed.

Run all tests in the Django container:

```bash
docker compose exec web python -m pytest -v
```

## Monitoring

- **Prometheus** collects application metrics.
- **Grafana** visualizes HTTP request rates, response latency, and errors.
- **Sentry** provides application error monitoring when configured.

Local monitoring interfaces are listed below. They are intended for development use.

## Running Locally

### Prerequisites

- Docker Desktop (or Docker Engine with Docker Compose)
- Git

### Setup

**1. Clone the repository**

```bash
git clone https://github.com/Ivan136dangeranger/gym-backend.git
cd gym-backend
```

**2. Create your environment configuration**

On Linux or macOS:

```bash
cp .env.example .env
```

On Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Set the following variables in `.env` (the example file provides placeholders):

```dotenv
DJANGO_SECRET_KEY=replace-with-your-own-generated-secret-key
DB_NAME=gym_db
DB_USER=gym_user
DB_PASSWORD=change-me
DB_HOST=db
DB_PORT=5432
SENTRY_DSN=
SENTRY_ENVIRONMENT=development
```

Generate a Django secret key locally; **do not commit it or share it publicly**:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

This command requires Django to be installed in the local Python environment. Alternatively, use a securely generated random secret. Keep the actual value only in `.env` or a secure secret manager.

**3. Build and start the containers**

```bash
docker compose up -d --build
```

**4. Apply database migrations**

```bash
docker compose exec web python manage.py migrate
```

**5. Verify the Django configuration**

```bash
docker compose exec web python manage.py check
```

**6. Run the tests (optional)**

```bash
docker compose exec web python -m pytest -v
```

### Local Services

| Service | URL |
| --- | --- |
| Django API | http://localhost:8000 |
| Prometheus | http://localhost:9090 |
| Grafana | http://localhost:3000 |
| RabbitMQ Management | http://localhost:15672 |

These addresses apply to the local Docker Compose development setup.

## Project Structure

```text
gym-backend/
├── clients/            # Client models, API, and tests
├── trainers/           # Trainer models and related code
├── subscriptions/      # Subscription API, business logic, tasks, and tests
├── dashboard/          # Dashboard-related application code
├── config/             # Django settings, URL routing, and Celery configuration
├── .dockerignore
├── .env.example        # Environment configuration template (no secrets)
├── .gitignore
├── Dockerfile
├── compose.yml         # Docker Compose services
├── manage.py
├── prometheus.yml      # Prometheus configuration
├── pytest.ini
├── requirements.txt
└── README.md
```

## Project Status and Next Steps

This is a **portfolio / learning project**, not a production-deployed service.

Planned improvements:

- Add continuous integration (for example, GitHub Actions).
- Deploy the API with production-grade settings and an appropriate application server.
- Replace the demo Celery email task with real email delivery.
- Extend API documentation with verified endpoint examples.

## Author

[GitHub — Ivan136dangeranger](https://github.com/Ivan136dangeranger)
