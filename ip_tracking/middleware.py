from datetime import datetime
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
        # One-time configuration and initialization.

    def __call__(self, request):
        ip_address = request.META.get('REMOTE_ADDR', '')
        geo_data = getattr(request, 'geolocation', None)

        if not geo_data:
            geo_data = {'country': 'Unknown', 'city': 'Unknown'}
            logger.warning(f"No geolocation data found for IP: {ip_address}")

        if ip_address:
            cache_key = f"geo_log_{ip_address}"
            if not cache.get(cache_key):
                logger.info(f"{datetime.now()} - Path: {request.path} - IP: {ip_address} - Geo: {geo_data}")
                cache.set(cache_key, True, timeout=86400)  # Cache flag only, not geo data itself
            else:
                logger.debug(f"Geo data for {ip_address} already logged recently.")

        logger.info(f"{datetime.now()} - Path: {request.path} - IP: {ip_address}")
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