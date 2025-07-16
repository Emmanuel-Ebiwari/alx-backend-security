from django.http import JsonResponse
from ratelimit.decorators import ratelimit

@ratelimit(key='user_or_ip', rate='10/m', block=True)
@ratelimit(key='ip', rate='5/m', block=True)
def my_view(request):
    return JsonResponse({"message": "Hello, world!"})
