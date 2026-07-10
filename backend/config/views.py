from django.http import JsonResponse


def api_home(request):
    return JsonResponse({
        "name": "APIHub Platform",
        "version": "v1",
        "status": "running",
    })