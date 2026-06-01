# Roommate Finder — Backend API

A production-grade Django REST API for finding compatible roommates through preference-based matching, real-time WebSocket chat, Celery background tasks, and SMS notifications via Africa's Talking.

> **Live API:** https://roommate-finder-web.onrender.com
> **API Docs:** https://roommate-finder-web.onrender.com/api/docs/
> **Frontend:** https://rommate-finder-frontend.vercel.app

![CI](https://github.com/Ab494/Roomate-Finder/actions/workflows/ci.yml/badge.svg)

---

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | Django 5 + Django REST Framework |
| Database | PostgreSQL 18 (Render) |
| Real-time | Django Channels + Daphne (WebSocket) |
| Background Tasks | Celery + Celery Beat + Redis |
| Cache / Broker | Redis (Valkey 8 on Render) |
| Media Storage | Cloudinary |
| SMS | Africa's Talking API |
| Auth | JWT — djangorestframework-simplejwt |
| API Docs | drf-spectacular (Swagger + ReDoc) |
| Containerisation | Docker multi-stage + Docker Compose |
| CI/CD | GitHub Actions → Docker Hub → Render |
| IaC | Terraform (Render provider) |
| Monitoring | UptimeRobot (5-min intervals) |

---

## Architecture

```
GitHub Push
        ↓
GitHub Actions CI
(lint → test → build → deploy)
        ↓
Docker Hub (image registry)
        ↓
Render (5 services)
├── roommate-finder-web      (Gunicorn / HTTP)
├── roommate-finder-channels (Daphne / WebSocket)
├── roommate-finder-worker   (Celery worker)
├── roommate-finder-beat     (Celery beat scheduler)
├── roommate-finder-db       (PostgreSQL 18)
└── roommate-finder-redis    (Valkey 8)
```

---

## Quick Start (Docker)

```bash
# 1. Clone the repo
git clone https://github.com/Ab494/Roomate-Finder.git
cd Roomate-Finder

# 2. Configure environment
cp .env.example .env
# Fill in your credentials in .env

# 3. Start all services
docker compose up --build

# 4. Run migrations and create superuser
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser

# 5. Verify everything is healthy
curl http://localhost:8000/api/health/
```

---

## Manual Setup (without Docker)

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env

python manage.py migrate
python manage.py runserver

# In separate terminals:
celery -A config worker --loglevel=info
celery -A config beat --loglevel=info --scheduler django_celery_beat.schedulers.DatabaseScheduler
```

---

## API Endpoints

| URL | Description |
|---|---|
| `/api/health/` | Health check — checks DB + Redis, returns 503 if degraded |
| `/api/docs/` | Swagger UI (interactive) |
| `/api/redoc/` | ReDoc |
| `/admin/` | Django Admin |
| `/api/auth/register/` | Register — returns JWT tokens + user object |
| `/api/auth/login/` | Login — returns JWT tokens + user object |
| `/api/auth/token/refresh/` | Refresh access token |
| `/api/auth/logout/` | Logout — blacklists refresh token |
| `/api/profiles/me/` | Get / update current user profile |
| `/api/profiles/location/` | Update user location (lat/lng) |
| `/api/listings/` | Browse and create room listings |
| `/api/listings/{id}/` | Listing detail, update, delete |
| `/api/listings/{id}/photos/` | Upload listing photos |
| `/api/matches/suggestions/` | Get ranked compatibility suggestions |
| `/api/matches/request/` | Send a match request |
| `/api/conversations/` | List conversations |
| `/api/conversations/{id}/messages/` | Get messages in a conversation |
| `/api/notifications/` | Notification feed |
| `/api/reviews/` | Create and view reviews |

---

## Matching Algorithm

Compatibility scores are calculated across 5 weighted criteria:

| Criterion | Max Points | What it checks |
|---|---|---|
| Budget overlap | 25 | How much rent ranges overlap |
| Gender preference | 20 | Preferred roommate gender match |
| Lifestyle | 25 | Sleep schedule, cleanliness, noise tolerance |
| Location proximity | 20 | Distance between preferred areas |
| Booleans | 10 | Smoking, pets, guests compatibility |
| **Total** | **100** | |

**Score labels:** 80–100 = Excellent · 60–79 = Good · 40–59 = Fair · 0–39 = Low

Scores are computed asynchronously via Celery and cached in Redis for 30 minutes.

---

## Project Structure

```
├── config/
│   ├── settings.py       # All settings with django-environ
│   ├── urls.py           # Root URL config
│   ├── asgi.py           # ASGI + Channels routing
│   ├── wsgi.py           # WSGI for Gunicorn
│   └── celery.py         # Celery app config
│
├── apps/
│   ├── profiles/         # Custom User model, Profiles, Preferences, Auth views
│   ├── listings/         # Room listings, photos, geo-search, filters
│   ├── matching/         # Compatibility algorithm + Celery tasks
│   ├── messaging/        # WebSocket consumers + REST message history
│   ├── location/         # Area and city reference data
│   ├── reviews/          # Star ratings and review reports
│   ├── notifications/    # In-app, SMS, and email notifications
│   ├── adminpanel/       # Platform stats and moderation endpoints
│   └── health/           # Liveness + readiness probe (/api/health/)
│
├── core/                 # Shared permissions, pagination, utilities
├── terraform/            # Render infrastructure as code
│   ├── main.tf
│   ├── variables.tf
│   ├── services.tf
│   └── outputs.tf
│
└── tests/                # pytest suite + factory-boy fixtures
    ├── factories.py
    ├── test_auth.py
    ├── test_listings.py
    ├── test_algorithm.py
    └── test_reviews.py
```

---

## Running Tests

```bash
source venv/bin/activate

# Run all tests
pytest tests/ -v

# With coverage
coverage run -m pytest tests/ -v
coverage report --fail-under=40
coverage html  # generates htmlcov/index.html
```

CI runs **33 tests** automatically on every push using real PostgreSQL and Redis service containers.

---

## DevOps — 7 Phases

| Phase | What was built |
|---|---|
| **1 — Git Strategy** | 3-branch model (main/staging/develop), conventional commits, .gitignore, .dockerignore |
| **2 — Docker** | Multi-stage Dockerfile, non-root user, healthchecks, fixed compose port mapping |
| **3 — CI/CD** | GitHub Actions: lint (flake8+black+isort) → test → build+push → deploy |
| **4 — Env Config** | REDIS_URL deduplication, Django 4.2 STORAGES dict, structured JSON logging |
| **5 — Render Deploy** | Blueprint via render.yaml — 5 services provisioned automatically |
| **6 — Health Checks** | /api/health/ checks DB + Redis, returns 503 if any dependency is degraded |
| **7 — Terraform** | Complete Render infrastructure described as code, reproducible with one command |

---

## Environment Variables

Copy `.env.example` to `.env` and fill in your values:

```env
# Django
SECRET_KEY=your-50-char-secret-key
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,.onrender.com
CORS_ALLOWED_ORIGINS=https://your-frontend.vercel.app

# Database
DB_NAME=roommate_finder
DB_USER=postgres
DB_PASSWORD=password
DB_HOST=db
DB_PORT=5432

# Redis
REDIS_URL=redis://redis:6379/0

# JWT
JWT_ACCESS_TOKEN_LIFETIME_MINUTES=60
JWT_REFRESH_TOKEN_LIFETIME_DAYS=7

# Cloudinary
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret

# Africa's Talking
AT_USERNAME=sandbox
AT_API_KEY=your-at-api-key

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

---

## GitHub Actions Secrets Required

| Secret | Description |
|---|---|
| `DOCKER_USERNAME` | Docker Hub username |
| `DOCKER_TOKEN` | Docker Hub access token (Read/Write) |
| `RENDER_API_KEY` | Render API key |
| `RENDER_SERVICE_ID` | Render web service ID (srv-xxx) |

---

## Author

**Evans Kipngeno Cheruiyot (Vanso)**
Full-stack Engineer and Educator — Nairobi, Kenya
GitHub: [@Ab494](https://github.com/Ab494)
Portfolio: [evanskip.netlify.app](https://evanskip.netlify.app)