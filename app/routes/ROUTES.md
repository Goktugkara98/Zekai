# Routes Architecture

This project uses a simple, two-folder route architecture to keep the codebase modular and easy to navigate:

- `api/` for JSON APIs
- `pages/` for HTML-rendered pages (server-side rendered routes)

## Structure

- `app/routes/`
  - `__init__.py` — Central registry exposing `register_blueprints(app)` which imports and registers all blueprints.
  - `api/`
    - `models.py`
    - `healthcheck.py` → blueprint `health` mounted at `/api/health`
    - `chats.py` → blueprint `chats` mounted at `/api/chats`
    - `categories.py`
    - `recommendations.py` → blueprint `recommendations` mounted at `/api/recommendations`
    - `admin.py` (moved from `admin/api.py`) — Admin JSON API endpoints mounted under `/admin/api/*`
  - `pages/`
    - `home.py` (moved from `main_routes.py`) → blueprint `main`
    - `auth.py` (moved from `auth.py`) → blueprint `auth`
    - `admin.py` (moved from `admin/pages.py`) → blueprint `admin`

Legacy files (to be removed after verification):

- `app/routes/main_routes.py`
- `app/routes/auth.py`
- `app/routes/admin/` (entire folder)
- `app/routes/pages/main_routes.py/` (stray empty directory)

## Registration

All blueprints are registered centrally in `app/routes/__init__.py` via `register_blueprints(app)`. Imports are kept inside the function to avoid circular imports and keep app startup simple.

```python
from app.routes import register_blueprints

app = Flask(__name__)
register_blueprints(app)
```

## Naming Conventions

- Blueprint names reflect the feature: `main`, `auth`, `admin`, `models`, `categories`, `chats`, `health`, `recommendations`, `admin_api`.
- URL prefixes
  - Pages: `/` (root), `/auth/*`, `/admin/*`
  - API: `/api/<feature>` (e.g., `/api/chats`, `/api/models`, `/api/categories`, `/api/recommendations`)
  - Admin API: `/admin/api/*`

## Testing

Validate app starts and routes resolve:

- Public pages: `/`, `/chat`, `/auth/login`, `/auth/register`
- APIs: `/api/health`, `/api/models`, `/api/chats/*`, `/api/categories`, `/api/recommendations`
- Admin: `/admin`, `/admin/api/*`

## Rationale

- Centralized registration simplifies app initialization and keeps a single source of truth for mounted routes.
- Two-folder model (`api/` and `pages/`) reduces cognitive load and avoids scattering admin-specific code in a separate top-level folder.

## Service Layer Organization

- Business services live under `app/services/` (e.g., `chat_service.py`, `model_service.py`).
- LLM/provider integrations are isolated under `app/services/providers/` to keep them decoupled from business logic:
  - `app/services/providers/gemini.py` → `GeminiService`
  - `app/services/providers/openrouter.py` → `OpenRouterService`
  - `app/services/providers/factory.py` → `ProviderFactory`

### Import examples

```python
# Use ProviderFactory inside business services
from app.services.providers.factory import ProviderFactory

# Direct provider usage (e.g., in recommendations)
from app.services.providers.gemini import GeminiService
```

This separation clarifies responsibilities: business logic in services/, provider-specific HTTP clients in services/providers/.
