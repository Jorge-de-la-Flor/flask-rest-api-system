README in [Spanish](README.es.md)

# Flask REST API System

Implemented JWT-based authentication with Werkzeug password hashing and 24-hour token expiration. Designed RESTful endpoints with role-based access control via decorator pattern. Persisted operations data in SQLite with proper transaction management and error handling. Developed a comprehensive test suite using pytest with 100% endpoint coverage. Tech stack: Flask, Werkzeug, PyJWT, SQLite3.

REST API in Flask with JWT authentication, user management, and persistent operations in SQLite.

## Characteristics

- Registration and login of users with hashed passwords (Werkzeug) and JWT with 24h expiration.
- SQLite database automatically initialized with `users` and `api_operations` tables.
- Decorator `@token_required` to protect endpoints and obtain the current user from the token.
- Endpoints to create and list authenticated user operations.
- Health endpoint `/api/status` and profile with activity statistics `/api/user/profile`.
- Tests with `pytest` and project managed via `pyproject.toml`.

## Main Endpoints

- `POST /api/register` – User registration.
- `POST /api/login` – Authentication and obtaining JWT.
- `GET /api/status` – Health check.
- `POST /api/operations` – Create operation (requires JWT).
- `GET /api/operations` – List user operations (requires JWT).
- `GET /api/user/profile` – Profile + operation statistics (requires JWT).

## Technical Stack

- Flask 3.x, Werkzeug, Jinja2.
- PyJWT for token generation and validation.
- SQLite3 for persistence.
- Pytest for testing.
