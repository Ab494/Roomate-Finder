# ── Stage 1: Builder ──────────────────────────────────────────────────────────
FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Build-time system deps (gcc needed to compile psycopg2, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Compile all dependencies into wheels (binary packages)
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip wheel --no-cache-dir --no-deps --wheel-dir /wheels -r requirements.txt


# ── Stage 2: Runtime ──────────────────────────────────────────────────────────
FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

WORKDIR /app

# Only runtime deps (no gcc)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user to run the app
RUN addgroup --system appgroup && \
    adduser --system --ingroup appgroup appuser

# Install pre-built wheels from Stage 1 (no recompiling)
COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir /wheels/*

# Copy project files
COPY . .

# Create folders and give ownership to appuser
RUN mkdir -p staticfiles media && \
    chown -R appuser:appgroup /app

# Switch to non-root user
USER appuser

EXPOSE 8000

# collectstatic and migrate run at STARTUP (env vars are available here)
CMD ["sh", "-c", "python manage.py migrate --noinput && \
                  python manage.py collectstatic --noinput && \
                  gunicorn config.wsgi:application \
                    --bind 0.0.0.0:${PORT} \
                    --workers 4 \
                    --threads 2 \
                    --timeout 120 \
                    --access-logfile - \
                    --error-logfile -"]
