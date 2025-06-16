# animals/urls.py (главный файл проекта)
from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('siteapp.urls')),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
    path('testing/', include('siteapp.non_api_urls')),

    path('silk/', include('silk.urls', namespace='silk')),
    re_path(r'^((?!media|silk).)*$', TemplateView.as_view(template_name='index.html'), name='app'),
]

# Для обслуживания медиа файлов в режиме DEBUG
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)