# siteapp/urls_api.py
from django.urls import path
from .views import HomePageDataAPIView # Убедитесь, что импорт правильный

urlpatterns = [
    path('homepage/', HomePageDataAPIView.as_view(), name='homepage_data_api'),
]