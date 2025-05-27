from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.password_validation import (
    MinimumLengthValidator,
    CommonPasswordValidator,
    NumericPasswordValidator,
    UserAttributeSimilarityValidator,
)


class CustomMinimumLengthValidator(MinimumLengthValidator):
    def __init__(self, min_length=8):
        super().__init__(min_length)

    def validate(self, password, user=None):
        if len(password) < self.min_length:
            raise ValidationError(
                _(
                    "Этот пароль слишком короткий. Он должен содержать как минимум %(min_length)d символов."
                ),
                code="password_too_short",
                params={"min_length": self.min_length},
            )

    def get_help_text(self):
        return _("Ваш пароль должен содержать как минимум %(min_length)d символов.") % {
            "min_length": self.min_length
        }


class CustomCommonPasswordValidator(CommonPasswordValidator):
    def validate(self, password, user=None):
        if password.lower().strip() in self.passwords:
            raise ValidationError(
                _("Этот пароль слишком широко распространён."),
                code="password_too_common",
            )

    def get_help_text(self):
        return _("Ваш пароль не может быть слишком широко распространённым.")


class CustomNumericPasswordValidator(NumericPasswordValidator):
    def validate(self, password, user=None):
        if password.isdigit():
            raise ValidationError(
                _("Этот пароль состоит только из цифр."),
                code="password_entirely_numeric",
            )

    def get_help_text(self):
        return _("Ваш пароль не может состоять только из цифр.")


class CustomUserAttributeSimilarityValidator(UserAttributeSimilarityValidator):

    def get_help_text(self):
        return _(
            "Ваш пароль не должен быть слишком похож на другую вашу личную информацию."
        )
