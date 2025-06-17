from typing import Type

from rest_framework import permissions


class IsOwnerOrAdminOrModeratorForComment(permissions.BasePermission):
    """
    Разрешает чтение всем.
    Создание: проверяется отдельно во View (IsAuthenticated).
    Редактирование: только владелец (если у его роли есть право can_edit_own_comment).
    Удаление: владелец (если can_delete_own_comment) ИЛИ пользователь с правом can_delete_any_comment ИЛИ is_staff.
    """

    def has_object_permission(self, request: Type, view: Type, obj: Type) -> bool:

        if request.method in permissions.SAFE_METHODS:
            return True

        if not request.user or not request.user.is_authenticated:
            return False

        if request.user.is_staff:
            return True

        user_role = request.user.role

        if request.method in ["PUT", "PATCH"]:

            return obj.user == request.user and (
                user_role and user_role.can_edit_own_comment
            )

        if request.method == "DELETE":

            if obj.user == request.user and (
                user_role and user_role.can_delete_own_comment
            ):
                return True

            if user_role and user_role.can_delete_any_comment:
                return True

        return False


class CanManageArticles(permissions.BasePermission):
    """
    Разрешает создание, редактирование, удаление статей на основе прав роли пользователя.
    Чтение разрешено всем.
    """

    def has_permission(self, request: Type, view: Type) -> bool:
        if request.method in permissions.SAFE_METHODS:
            return True

        if request.method == "POST":

            if not (request.user and request.user.is_authenticated):
                return False

            if request.user.is_staff:
                return True

            if hasattr(request.user, "role") and request.user.role:
                return request.user.role.can_create_article

            return False

        return request.user and request.user.is_authenticated

    def has_object_permission(self, request: Type, view: Type, obj: Type) -> bool:

        if request.method in permissions.SAFE_METHODS:
            return True
        if not (request.user and request.user.is_authenticated):
            return False

        if request.user.is_staff:
            return True

        if request.user.role:
            if request.method in ["PUT", "PATCH"]:

                if (
                    obj.author == request.user
                    and request.user.role.can_edit_own_article
                ):
                    return True

                if request.user.role.can_edit_any_article:
                    return True
            elif request.method == "DELETE":
                if (
                    obj.author == request.user
                    and request.user.role.can_delete_own_article
                ):
                    return True
                if request.user.role.can_delete_any_article:
                    return True
        return False


class CanManageAdvertisements(permissions.BasePermission):
    """
    Разрешает чтение всем.
    Создание: зависит от права can_create_advertisement у роли пользователя.
    Редактирование/Удаление:
        - Владелец: если есть права can_edit_own_advertisement / can_delete_own_advertisement.
        - Модератор/Админ: если есть право can_manage_any_advertisement ИЛИ is_staff.
    """

    def has_permission(self, request: Type, view: Type) -> bool:
        if request.method in permissions.SAFE_METHODS:
            return True

        if not request.user or not request.user.is_authenticated:
            return False

        if request.method == "POST":
            if request.user.is_staff:
                return True
            if request.user.role:
                return request.user.role.can_create_advertisement
            return False

        return True

    def has_object_permission(self, request: Type, view: Type, obj: Type) -> bool:
        if request.method in permissions.SAFE_METHODS:
            return True

        if not request.user or not request.user.is_authenticated:
            return False

        if request.user.is_staff:
            return True

        user_role = request.user.role

        if obj.user == request.user:
            if request.method in ["PUT", "PATCH"]:
                return user_role and user_role.can_edit_own_advertisement
            elif request.method == "DELETE":
                return user_role and user_role.can_delete_own_advertisement

        if user_role and user_role.can_manage_any_advertisement:

            if request.method in ["PUT", "PATCH", "DELETE"]:
                return True

        return False


class IsOwnerOrAdminOrReadOnly(permissions.BasePermission):
    """
    Разрешает чтение всем (GET, HEAD, OPTIONS).
    Разрешает создание, если пользователь аутентифицирован (проверяется отдельно во ViewSet для create).
    Разрешает редактирование (PUT, PATCH) и удаление (DELETE) только владельцу объекта или администратору (is_staff).
    """

    def has_permission(self, request: Type, view: Type) -> bool:
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request: Type, view: Type, obj: Type) -> bool:
        if request.method in permissions.SAFE_METHODS:
            return True
        if hasattr(obj, 'user'):
            return obj.user == request.user or request.user.is_staff
        return request.user.is_staff
        
class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Разрешает доступ владельцу объекта или администратору.
    """
    def has_object_permission(self, request: Type, view: Type, obj: Type) -> bool:
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj == request.user or request.user.is_staff

