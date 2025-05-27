from django.dispatch import receiver
from djoser.signals import user_registered
from .models import Role, User


# Без этого роль на пользователя не создаётся
@receiver(user_registered)
def assign_default_role_on_registration(sender, user, request, **kwargs):
    try:
        if not user.role:
            default_role, created = Role.objects.get_or_create(
                name="Пользователь",
                defaults={
                    "can_create_advertisement": True,
                    "can_edit_own_advertisement": True,
                    "can_delete_own_advertisement": True,
                    "can_edit_own_comment": True,
                    "can_delete_own_comment": True,
                },
            )
            if created:
                print(f"Default role 'Пользователь' was created by signal handler.")
            user.role = default_role
            user.save(update_fields=["role"])
            print(
                f"Assigned default role '{user.role.name}' to user {user.email} via signal."
            )
    except Role.DoesNotExist:
        print(
            f"ERROR (Signal): Default role 'Пользователь' not found. User {user.email} was not assigned a role."
        )
    except Exception as e:
        print(
            f"ERROR (Signal): Could not assign default role to user {user.email}. Error: {e}"
        )
