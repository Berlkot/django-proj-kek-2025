from django.shortcuts import redirect
from django.urls import reverse
from social_core.pipeline.user import user_details
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings

from .models import User, Role


def set_user_defaults(strategy, details: dict, user: User = None, *args, **kwargs) -> None:
    """
    Устанавливает значения по умолчанию для нового пользователя,
    созданного через социальные сети.
    """
    if user and kwargs.get('is_new', False):
        if not user.display_name:
            full_name = details.get('fullname') or f"{details.get('first_name', '')} {details.get('last_name', '')}".strip()
            user.display_name = full_name or user.username
        
        try:
            default_role, _ = Role.objects.get_or_create(name="Пользователь")
            user.role = default_role
        except Exception as e:
            print(f"Could not assign default role during social auth: {e}")
            
        user.save()

def generate_jwt_and_redirect(backend, user, response, *args, **kwargs):
    """
    Генерирует JWT токены для пользователя и выполняет редирект
    на фронтенд-страницу-колбэк, добавляя токены в хэш URL.
    """
    if user and backend.name in ['google-oauth2', 'vk-oauth2']:
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        # ВАЖНО: Указываем полный URL фронтенд-колбэка
        # Это тот самый URL, который теперь будет обрабатывать Vue
        frontend_callback_url = f"{settings.FRONTEND_BASE_URL}social/auth/callback/"
        

        final_url = f"{frontend_callback_url}?access={access_token}&refresh={refresh_token}"
        print(f"Redirecting to: {final_url}")
        
        return redirect(final_url)

    return None