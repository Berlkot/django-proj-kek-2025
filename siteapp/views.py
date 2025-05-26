# siteapp/views.py
from django.shortcuts import redirect, Http404
from django.urls import reverse
from django.conf import settings
from .models import Advertisement

FRONTEND_BASE_URL = getattr(settings, 'FRONTEND_BASE_URL', 'http://localhost:5173')

def latest_advertisement_redirect_view(request):
    latest_ad = Advertisement.objects.order_by('-publication_date').first()
    if latest_ad:
        frontend_url = f"{FRONTEND_BASE_URL}advertisement/{latest_ad.pk}"
        return redirect(frontend_url)
    else:
        raise Http404("Объявления не найдены для редиректа.")

def page_needs_login_view(request):
    if not request.user.is_authenticated:
        login_url_frontend = f"{FRONTEND_BASE_URL}login?next={request.path}"
        return redirect(login_url_frontend)
    from django.http import HttpResponse
    return HttpResponse(f"Привет, {request.user.username}! Это защищенная страница на Django.")