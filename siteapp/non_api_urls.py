# siteapp/non_api_urls.py
from django.urls import path
from . import views


urlpatterns = [
    path('latest-ad-redirect/', views.latest_advertisement_redirect_view, name='latest_ad_redirect'),
    path('protected-page/', views.page_needs_login_view, name='protected_page'),
]