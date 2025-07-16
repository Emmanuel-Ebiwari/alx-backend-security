from datetime import datetime, timezone
import logging
from django.http import HttpResponse
from django.core.cache import cache
import time
from .model import BlockedIP

logger = logging.getLogger(__name__)
handler = logging.FileHandler('requests.log')
formatter = logging.Formatter('%(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        ip_address = request.META.get('REMOTE_ADDR', '')
        geo_data = getattr(request, 'geolocation', None)

        if not geo_data:
            geo_data = {'country': 'Unknown', 'city': 'Unknown'}
            logger.warning(f"No geolocation data found for IP: {ip_address}")

        # Existing geo log
        cache_key = f"geo_log_{ip_address}"
        if not cache.get(cache_key):
            logger.info(f"{datetime.now()} - Path: {request.path} - IP: {ip_address} - Geo: {geo_data}")
            cache.set(cache_key, True, timeout=86400)

        # Track request paths and timestamps for later checking
        if ip_address:
            request_log_key = f"request_logs_{ip_address}"
            logs = cache.get(request_log_key, [])
            logs.append({"path": request.path, "time": datetime.now(timezone.utc).isoformat()})
            cache.set(request_log_key, logs, timeout=3600)  # Keep logs for 1 hour

            # Maintain active IP list
            tracked_ips = cache.get("tracked_ips", set())
            tracked_ips.add(ip_address)
            cache.set("tracked_ips", tracked_ips, timeout=3600)

        response = self.get_response(request)
        return response

class BlockIpMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        ip_address = request.META.get('REMOTE_ADDR', '')
        blocked_ip = BlockedIP.objects.filter(ip_address=ip_address).first()
        if blocked_ip:
            return HttpResponse("Your IP has been blocked.", status=403)
        
        response = self.get_response(request)
        return response