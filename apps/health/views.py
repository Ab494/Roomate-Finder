import logging
import time

from django.core.cache import cache
from django.db import connection
from django.http import JsonResponse

logger = logging.getLogger(__name__)


def health_check(request):
    """
    Liveness + readiness probe.
    Checks DB and Redis. Returns 503 if either is down.
    """
    start = time.time()
    checks = {}
    status = 200

    # ── Database check ────────────────────────────────────────────────────────
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        checks["database"] = "ok"
    except Exception as exc:
        checks["database"] = f"error: {exc}"
        status = 503
        logger.error("Health check: database unreachable", exc_info=True)

    # ── Redis / Cache check ───────────────────────────────────────────────────
    try:
        cache.set("health_ping", "pong", timeout=5)
        assert cache.get("health_ping") == "pong"
        checks["cache"] = "ok"
    except Exception as exc:
        checks["cache"] = f"error: {exc}"
        status = 503
        logger.error("Health check: Redis unreachable", exc_info=True)

    elapsed = round((time.time() - start) * 1000, 2)

    payload = {
        "status": "healthy" if status == 200 else "degraded",
        "checks": checks,
        "response_time_ms": elapsed,
    }

    logger.info("Health check", extra={"status": payload["status"], "response_time_ms": elapsed})
    return JsonResponse(payload, status=status)
