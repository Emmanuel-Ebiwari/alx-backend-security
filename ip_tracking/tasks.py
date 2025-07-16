from celery import shared_task
from django.core.cache import cache
from datetime import datetime, timedelta, timezone
from .models import SuspiciousIP

@shared_task
def flag_suspicious_ips():
    tracked_ips = cache.get("tracked_ips", set())
    now = now = datetime.now(timezone.utc)
    one_hour_ago = now - timedelta(hours=1)

    for ip in tracked_ips:
        logs = cache.get(f"request_logs_{ip}", [])

        recent_logs = [
            log for log in logs
            if datetime.fromisoformat(log['time']) > one_hour_ago
        ]

        # Check for excessive requests
        if len(recent_logs) > 100:
            SuspiciousIP.objects.get_or_create(ip_address=ip, reason="Over 100 requests/hour")
            continue

        # Check for sensitive path access
        sensitive_paths = ['/admin', '/login']
        if any(any(log['path'].startswith(p) for p in sensitive_paths) for log in recent_logs):
            SuspiciousIP.objects.get_or_create(ip_address=ip, reason="Accessed sensitive path")
