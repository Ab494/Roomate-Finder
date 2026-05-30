# ── PostgreSQL ─────────────────────────────────────────────────────────────────
resource "render_postgres" "db" {
  name          = "roommate-finder-db"
  region        = "oregon"
  plan          = "starter"
  version       = "16"
  database_name = "roommate_finder"
  database_user = "roommate_user"
}

# ── Redis ──────────────────────────────────────────────────────────────────────
resource "render_redis" "cache" {
  name              = "roommate-finder-redis"
  region            = "oregon"
  plan              = "starter"
  max_memory_policy = "allkeys_lru"
}

# ── Web service (Gunicorn) ─────────────────────────────────────────────────────
resource "render_web_service" "web" {
  name          = "roommate-finder-web"
  region        = "oregon"
  plan          = "starter"
  start_command = "gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --threads 2 --timeout 120 --access-logfile - --error-logfile -"

  runtime_source = {
    native_runtime = {
      auto_deploy   = true
      branch        = "main"
      build_command = "./build.sh"
      repo_url      = "https://github.com/Ab494/Roomate-Finder"
      runtime       = "python"
    }
  }

  env_vars = {
    PYTHON_VERSION = { value = "3.12" }
    DEBUG          = { value = "False" }
    SECRET_KEY     = { value = var.secret_key }
    ALLOWED_HOSTS  = { value = ".onrender.com" }

    DATABASE_URL = { value = render_postgres.db.connection_info.internal_connection_string }
    REDIS_URL    = { value = render_redis.cache.connection_info.internal_connection_string }

    CLOUDINARY_CLOUD_NAME = { value = var.cloudinary_cloud_name }
    CLOUDINARY_API_KEY    = { value = var.cloudinary_api_key }
    CLOUDINARY_API_SECRET = { value = var.cloudinary_api_secret }
    AT_API_KEY            = { value = var.at_api_key }
    EMAIL_HOST_USER       = { value = var.email_host_user }
    EMAIL_HOST_PASSWORD   = { value = var.email_host_password }
  }

  health_check_path = "/api/health/"
}

# ── Celery worker ──────────────────────────────────────────────────────────────
resource "render_background_worker" "worker" {
  name          = "roommate-finder-worker"
  region        = "oregon"
  plan          = "starter"
  start_command = "celery -A config worker --loglevel=info --concurrency=2"

  runtime_source = {
    native_runtime = {
      auto_deploy   = true
      branch        = "main"
      build_command = "pip install -r requirements.txt"
      repo_url      = "https://github.com/Ab494/Roomate-Finder"
      runtime       = "python"
    }
  }

  env_vars = {
    SECRET_KEY   = { value = var.secret_key }
    DATABASE_URL = { value = render_postgres.db.connection_info.internal_connection_string }
    REDIS_URL    = { value = render_redis.cache.connection_info.internal_connection_string }
  }
}

# ── Celery beat ────────────────────────────────────────────────────────────────
resource "render_background_worker" "beat" {
  name          = "roommate-finder-beat"
  region        = "oregon"
  plan          = "starter"
  start_command = "celery -A config beat --loglevel=info --scheduler django_celery_beat.schedulers.DatabaseScheduler"

  runtime_source = {
    native_runtime = {
      auto_deploy   = true
      branch        = "main"
      build_command = "pip install -r requirements.txt"
      repo_url      = "https://github.com/Ab494/Roomate-Finder"
      runtime       = "python"
    }
  }

  env_vars = {
    SECRET_KEY   = { value = var.secret_key }
    DATABASE_URL = { value = render_postgres.db.connection_info.internal_connection_string }
    REDIS_URL    = { value = render_redis.cache.connection_info.internal_connection_string }
  }
}
