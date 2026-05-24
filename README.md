# FastAPI Education Platform

Demo user-management API built with FastAPI, PostgreSQL, SQLAlchemy async sessions, Alembic migrations, and JWT bearer authentication.

The project exposes a small account API: create a user, log in with email/password, read or update the authenticated user profile, soft-delete users, and check service health.

## Features

- FastAPI application with OpenAPI docs at `/docs`
- PostgreSQL persistence
- Async SQLAlchemy database access
- Alembic migrations
- JWT access tokens via OAuth2 password flow
- Role-aware access checks for cross-user operations
- Soft delete via `is_active = false`
- Docker Compose demo setup

## Quick Start With Docker

The demo compose file starts PostgreSQL and the API. The API container runs migrations automatically before starting the server.

```bash
docker compose -f docker-compose-ci.yaml up -d --build
```

Or use the Makefile shortcut:

```bash
make run
```

The API will be available at:

```text
http://localhost:8000
```

Useful URLs:

- Health check: `GET http://localhost:8000/ping`
- Swagger UI: `http://localhost:8000/docs`
- OpenAPI schema: `http://localhost:8000/openapi.json`

Stop the demo stack:

```bash
docker compose -f docker-compose-ci.yaml down
```

## Local Database Stack

For local development databases only:

```bash
make up
```

This starts the local PostgreSQL services from `docker-compose-local.yaml`. It does not start the FastAPI app.

Stop local services:

```bash
make down
```

## Environment Variables

Copy `.env.example` to `.env` for local development:

```bash
cp .env.example .env
```

Required for application runtime:

| Variable | Purpose | Example |
| --- | --- | --- |
| `REAL_DATABASE_URL` | Async SQLAlchemy database URL for the app | `postgresql+asyncpg://app_user:change_me@localhost:5432/app_db` |
| `SECRET_KEY` | JWT signing secret | `replace-with-a-long-random-secret` |

Optional runtime variables:

| Variable | Purpose | Default |
| --- | --- | --- |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | JWT lifetime in minutes | `30` |
| `APP_PORT` | Port used by `python main.py` | `8000` |
| `ALGORITHM` | JWT signing algorithm | `HS256` |

Test/development variables:

| Variable | Purpose |
| --- | --- |
| `TEST_DATABASE_URL` | Async database URL used by tests |
| `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` | App database container credentials |
| `POSTGRES_TEST_USER`, `POSTGRES_TEST_PASSWORD`, `POSTGRES_TEST_DB` | Test database container credentials |

The Docker demo compose file provides safe demo defaults, including `SECRET_KEY=demo-secret-change-me`. Override `SECRET_KEY` for anything other than a local demo.

## Migrations

Apply migrations manually:

```bash
alembic upgrade head
```

The Docker image command already runs:

```bash
alembic upgrade head && python main.py
```

## Run The API Locally

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Set environment variables, apply migrations, then start the app:

```bash
alembic upgrade head
python main.py
```

## Run Tests

Start the local test database first:

```bash
make up
```

Then run:

```bash
pytest -q
```

Tests expect a reachable PostgreSQL test database configured by `TEST_DATABASE_URL` or `.env`.

## Main Endpoints

| Method | Path | Auth | Description |
| --- | --- | --- | --- |
| `GET` | `/ping` | No | Health check |
| `POST` | `/user/` | No | Create a user |
| `POST` | `/login/token` | No | Get a JWT access token |
| `GET` | `/user/?user_id=<uuid>` | Bearer token | Read a user profile if permitted |
| `PATCH` | `/user/?user_id=<uuid>` | Bearer token | Update a user profile if permitted |
| `DELETE` | `/user/?user_id=<uuid>` | Bearer token | Soft-delete a user if permitted |

## Demo Flow

There are no pre-seeded demo credentials. Create a user first, then use that email and password to log in.

Create a user:

```bash
curl -X POST http://localhost:8000/user/ \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"Demo\",\"surname\":\"User\",\"email\":\"demo@example.com\",\"password\":\"demo-password\"}"
```

Log in:

```bash
curl -X POST http://localhost:8000/login/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=demo@example.com&password=demo-password"
```

Use the returned `access_token`:

```bash
curl http://localhost:8000/user/?user_id=<user_id> \
  -H "Authorization: Bearer <access_token>"
```

Update the current user:

```bash
curl -X PATCH http://localhost:8000/user/?user_id=<user_id> \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"Updated\",\"surname\":\"User\"}"
```

Soft-delete the current user:

```bash
curl -X DELETE http://localhost:8000/user/?user_id=<user_id> \
  -H "Authorization: Bearer <access_token>"
```

After soft deletion, the user cannot log in again and existing bearer tokens are rejected.

## Notes

- User emails are unique. Duplicate email create/update attempts return `409 Conflict`.
- Regular users can operate on their own profile.
- Admin and superadmin roles are represented in the database as `ROLE_PORTAL_ADMIN` and `ROLE_PORTAL_SUPERADMIN`.
- New users created through the public API receive `ROLE_PORTAL_USER`.
