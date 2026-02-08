README en [inglés](README.md)

# Flask REST API System

Implementé autenticación JWT con contraseñas hasheadas usando Werkzeug y tokens con expiración de 24 horas. Diseñé endpoints RESTful con control de acceso basado en roles mediante un decorador. Persistí las operaciones en SQLite con gestión adecuada de transacciones y manejo de errores. Desarrollé una suite de pruebas completa con pytest con 100% de cobertura de endpoints. Stack tecnológico: Flask, Werkzeug, PyJWT, SQLite3.

API REST en Flask con autenticación JWT, gestión de usuarios y operaciones persistidas en SQLite.

## Características

- Registro y login de usuarios con contraseñas hasheadas (Werkzeug) y JWT con expiración de 24h.
- Base de datos SQLite inicializada automáticamente con tablas `users` y `api_operations`.
- Decorador `@token_required` para proteger endpoints y obtener el usuario actual desde el token.
- Endpoints para crear y listar operaciones del usuario autenticado.
- Endpoint de salud `/api/status` y perfil con estadísticas de actividad `/api/user/profile`.
- Tests con `pytest` y proyecto gestionado vía `pyproject.toml`.

## Endpoints principales

- `POST /api/register` – Registro de usuario.
- `POST /api/login` – Autenticación y obtención de JWT.
- `GET /api/status` – Health check.
- `POST /api/operations` – Crear operación (requiere JWT).
- `GET /api/operations` – Listar operaciones del usuario (requiere JWT).
- `GET /api/user/profile` – Perfil + estadísticas de operaciones (requiere JWT).

## Stack técnico

- Flask 3.x, Werkzeug, Jinja2.
- PyJWT para generación y validación de tokens.
- SQLite3 para persistencia.
- Pytest para pruebas.
