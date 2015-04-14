from django.conf import settings

def api_host(request):
    return {"API_HOST": settings.API_HOST}

