from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include("siteapp.urls")), # Предполагается, что вы создадите urls_api.py для DRF
    # ... другие API эндпоинты ...

    # Эта строка должна быть ПОСЛЕ всех API эндпоинтов
    # Она отдает управление Vue Router для всех остальных путей
    re_path(r'^.*$', TemplateView.as_view(template_name='index.html'), name='app'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)