# Roommate Finder

A full-stack Django backend for finding compatible roommates through preference-based matching, real-time chat, and SMS notifications.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Framework | Django 5.x + Django REST Framework |
| Database | PostgreSQL 16 |
| Real-time | Django Channels + Redis (WebSocket) |
| Async Tasks | Celery + Redis |
| SMS | Africa's Talking API |
| Media | Cloudinary |
| Auth | JWT (djangorestframework-simplejwt) |
| API Docs | drf-spectacular (Swagger + ReDoc) |
| Deployment | Docker + Nginx + Railway/Render |

## Quick Start (Docker)

```bash
# 1. Clone and enter directory
git clone https://github.com/yourname/roommate_finder.git
cd roommate_finder

# 2. Configure environment
cp .env.example .env
# Edit .env with your credentials

# 3. Start all services
docker-compose up --build

# 4. Run migrations + create superuser
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
```

## API Endpoints

| URL | Description |
|-----|-------------|
| http://localhost:8000/api/docs/ | Swagger UI |
| http://localhost:8000/api/redoc/ | ReDoc |
| http://localhost:8000/admin/ | Django Admin |
| ws://localhost:80/ws/chat/{id}/ | WebSocket Chat |

## Manual Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # configure .env
python manage.py migrate
python manage.py runserver

# In separate terminals:
celery -A config worker --loglevel=info
celery -A config beat --loglevel=info
```

## Running Tests

```bash
pytest
# With coverage
coverage run -m pytest && coverage report -m
```

## Project Structure

```
roommate_finder/
├── config/          # Settings, URLs, ASGI, Celery
├── apps/
│   ├── profiles/    # Auth, User model, Profiles, Preferences
│   ├── listings/    # Room listings, photos, geo-search
│   ├── matching/    # Scoring algorithm + Celery tasks
│   ├── messaging/   # WebSocket chat + REST history
│   ├── location/    # Area/city reference data
│   ├── reviews/     # Star ratings + review reports
│   ├── notifications/ # In-app + SMS + email notifications
│   └── adminpanel/  # Platform stats + moderation
├── core/            # Permissions, pagination, utilities
└── tests/           # pytest test suite + factories
```

## Matching Algorithm

Compatibility scores are calculated across 5 weighted criteria:

| Criterion | Max Points |
|-----------|-----------|
| Budget range overlap | 25 |
| Gender preference | 20 |
| Lifestyle (sleep/cleanliness/noise) | 25 |
| Location proximity | 20 |
| Booleans (smoking/pets/guests) | 10 |

Scores are computed async via Celery and cached in Redis for 30 minutes.

## Environment Variables

See `.env.example` for the full list of required variables including:
- Django `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`
- PostgreSQL connection details
- Redis URL
- Cloudinary credentials
- Africa's Talking API key
- SMTP email settings
- JWT token lifetimes
