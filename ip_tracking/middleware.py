from datetime import datetime
import logging
from django.http import HttpResponse
from django.core.cache import cache
import time

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
        logger.info(f"{datetime.now()} - Path: {request.path} - IP: {ip_address}")
        response = self.get_response(request)
        return response