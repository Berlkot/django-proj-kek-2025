from django.urls import path
from . import views
from django.http import JsonResponse

def health_check(request):
    """Простой эндпоинт для проверки здоровья."""
    return JsonResponse({"status": "ok"})

urlpatterns = [
    path('latest-ad-redirect/', views.latest_advertisement_redirect_view, name='latest_ad_redirect'),
    path('protected-page/', views.page_needs_login_view, name='protected_page'),
    path('health/', health_check, name='health_check'),
]