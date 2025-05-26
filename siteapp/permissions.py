# siteapp/permissions.py
from rest_framework import permissions

class IsOwnerOrAdminOrModeratorForComment(permissions.BasePermission):
    """
    Разрешает чтение всем.
    Создание: проверяется отдельно во View (IsAuthenticated).
    Редактирование: только владелец (если у его роли есть право can_edit_own_comment).
    Удаление: владелец (если can_delete_own_comment) ИЛИ пользователь с правом can_delete_any_comment (модератор) ИЛИ is_staff.
    """
    def has_object_permission(self, request, view, obj): # obj здесь - это AdResponse или Comment
        # Разрешение на чтение для всех
        if request.method in permissions.SAFE_METHODS:
            return True

        # Пользователь должен быть аутентифицирован для любых других действий
        if not request.user or not request.user.is_authenticated:
            return False

        # Суперпользователь Django может всё
        if request.user.is_staff:
            return True

        # Проверяем права на основе роли пользователя
        user_role = request.user.role

        if request.method in ['PUT', 'PATCH']: # Редактирование
            # Только владелец может редактировать, если его роль это позволяет
            return obj.user == request.user and (user_role and user_role.can_edit_own_comment)

        if request.method == 'DELETE': # Удаление
            # Владелец может удалить, если его роль это позволяет
            if obj.user == request.user and (user_role and user_role.can_delete_own_comment):
                return True
            # Пользователь с правом удалять любые комментарии (модератор)
            if user_role and user_role.can_delete_any_comment:
                return True
        
        return False

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
        if request.method in permissions.SAFE_METHODS: # GET, HEAD, OPTIONS
            return True

        # Для создания (POST)
        if request.method == 'POST':
            # Пользователь должен быть аутентифицирован
            if not (request.user and request.user.is_authenticated):
                return False
            
            # Администратор Django (is_staff) всегда должен иметь право создавать
            if request.user.is_staff:
                return True 
            
            # Если пользователь не админ Django, проверяем права его роли
            if hasattr(request.user, 'role') and request.user.role: # Убедимся, что role существует
                return request.user.role.can_create_article
            
            return False # Если нет роли или права в роли
        
        # Для PUT, PATCH, DELETE проверка будет в has_object_permission
        return request.user and request.user.is_authenticated # Должен быть аутентифицирован для доступа к has_object_permission

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
        
class CanManageAdvertisements(permissions.BasePermission):
    """
    Разрешает чтение всем.
    Создание: зависит от права can_create_advertisement у роли пользователя.
    Редактирование/Удаление:
        - Владелец: если есть права can_edit_own_advertisement / can_delete_own_advertisement.
        - Модератор/Админ: если есть право can_manage_any_advertisement ИЛИ is_staff.
    """
    def has_permission(self, request, view): # Для ListCreate views
        if request.method in permissions.SAFE_METHODS: # GET, HEAD, OPTIONS
            return True
        
        if not request.user or not request.user.is_authenticated:
            return False

        # Для создания (POST)
        if request.method == 'POST':
            if request.user.is_staff: # Django админ может создавать
                return True
            if request.user.role:
                return request.user.role.can_create_advertisement
            return False # Если нет роли или права
        
        return True # Для PUT, PATCH, DELETE проверка будет в has_object_permission

    def has_object_permission(self, request, view, obj): # obj - это Advertisement
        if request.method in permissions.SAFE_METHODS:
            return True

        if not request.user or not request.user.is_authenticated:
            return False
        
        if request.user.is_staff: # Django админ может всё с объектом
            return True

        user_role = request.user.role

        # Владелец
        if obj.user == request.user:
            if request.method in ['PUT', 'PATCH']: # Редактирование
                return user_role and user_role.can_edit_own_advertisement
            elif request.method == 'DELETE': # Удаление
                return user_role and user_role.can_delete_own_advertisement
        
        # Модерация (управление любыми объявлениями)
        if user_role and user_role.can_manage_any_advertisement:
            # Модератор с этим правом может редактировать и удалять любые объявления
            if request.method in ['PUT', 'PATCH', 'DELETE']:
                return True
        
        return False
