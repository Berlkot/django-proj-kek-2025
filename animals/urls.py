# animals/urls.py (главный файл проекта)
from django.contrib import admin
from django.urls import path, include, re_path # Добавлен include
from django.views.generic import TemplateView
from django.conf import settings # Для MEDIA_URL
from django.conf.urls.static import static # Для MEDIA_URL

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('siteapp.urls')),

    re_path(r'^((?!media).)*$', TemplateView.as_view(template_name='index.html'), name='app'),
]

# Для обслуживания медиа файлов в режиме DEBUG
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)