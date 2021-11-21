from django.http import HttpResponse


class HealthCheckMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path == "/health_check":
            return HttpResponse(status=200)
        return self.get_response(request)
