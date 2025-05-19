# siteapp/permissions.py
from rest_framework import permissions

class IsOwnerOrAdminOrReadOnly(permissions.BasePermission):
    """
    Разрешает чтение всем.
    Разрешает редактирование и удаление только владельцу объекта или администратору.
    """
    def has_object_permission(self, request, view, obj):
        # Разрешение на чтение для всех (GET, HEAD, OPTIONS запросы)
        if request.method in permissions.SAFE_METHODS:
            return True

        # Разрешение на запись только для владельца комментария или админа
        return obj.user == request.user or request.user.is_staff


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Разрешает чтение всем.
    Разрешает любые действия (включая удаление чужих) только администратору.
    """
    def has_permission(self, request, view): # Для list view (не используется для AdResponse напрямую)
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        # Для удаления и изменения - только админ
        return request.user and request.user.is_staff

class CanManageArticles(permissions.BasePermission):
    """
    Разрешает создание, редактирование, удаление статей на основе прав роли пользователя.
    Чтение разрешено всем.
    """
    def has_permission(self, request, view):
        # Разрешение на чтение (GET, HEAD, OPTIONS) для всех
        if request.method in permissions.SAFE_METHODS:
            return True

        # Для создания (POST)
        if request.method == 'POST':
            if request.user and request.user.is_authenticated and request.user.role:
                return request.user.role.can_create_article or request.user.is_staff
            return False
        
        # Для других методов (PUT, PATCH, DELETE) проверка будет на уровне объекта
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Разрешение на чтение объекта (GET, HEAD, OPTIONS) для всех
        if request.method in permissions.SAFE_METHODS:
            return True
        if not (request.user and request.user.is_authenticated):
            return False
        
        # Администраторы могут все
        if request.user.is_staff:
            return True

        # Проверка прав роли
        if request.user.role:
            if request.method in ['PUT', 'PATCH']: # Редактирование
                # obj здесь - это Article
                # Если автор статьи совпадает с текущим пользователем И роль позволяет редактировать свои
                if obj.author == request.user and request.user.role.can_edit_own_article:
                    return True
                # Если роль позволяет редактировать любые статьи
                if request.user.role.can_edit_any_article:
                    return True
            elif request.method == 'DELETE': # Удаление
                if obj.author == request.user and request.user.role.can_delete_own_article:
                    return True
                if request.user.role.can_delete_any_article:
                    return True
        return False