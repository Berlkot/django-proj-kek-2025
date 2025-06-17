# animals/urls.py (главный файл проекта)
from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/social/', include('social_django.urls', namespace='social')),
    path('social-auth-success/', TemplateView.as_view(template_name="social_auth_success.html"), name="social_auth_success"), 
    path('api/', include('siteapp.urls')),
    path('api/auth/', include('djoser.urls')),
    path('api/auth/', include('djoser.urls.jwt')),
    path('testing/', include('siteapp.non_api_urls')),

    path('silk/', include('silk.urls', namespace='silk')),
    re_path(r'^((?!media|silk|health).)*$', TemplateView.as_view(template_name='index.html'), name='app'),
]

# Для обслуживания медиа файлов в режиме DEBUG
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)