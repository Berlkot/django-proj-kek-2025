from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.password_validation import (
    MinimumLengthValidator,
    CommonPasswordValidator,
    NumericPasswordValidator,
    UserAttributeSimilarityValidator,
)


class CustomMinimumLengthValidator(MinimumLengthValidator):
    """
    Проверяет, что пароль имеет минимальную длину.
    """

    def __init__(self, min_length: int = 8):
        """
        Инициализирует валидатор пароля с минимальной длиной.

        :param min_length: Минимальная длина пароля.
        """
        super().__init__(min_length)

    def validate(self, password: str, user=None) -> None:
        """
        Проверяет пароль на соответствие минимальной длине.

        :param password: Пароль, который нужно проверить.
        :param user: Пользователь, для которого пароль предназначен.
        :raises ValidationError: Если пароль слишком короткий.
        """
        if len(password) < self.min_length:
            raise ValidationError(
                _(
                    "Этот пароль слишком короткий. Он должен содержать как минимум %(min_length)d символов."
                ),
                code="password_too_short",
                params={"min_length": self.min_length},
            )

    def get_help_text(self) -> str:
        """
        Возвращает текст, который может помочь пользователю в выборе пароля.

        :return: Текст, который может помочь пользователю в выборе пароля.
        """
        return _("Ваш пароль должен содержать как минимум %(min_length)d символов.") % {
            "min_length": self.min_length
        }


class CustomCommonPasswordValidator(CommonPasswordValidator):
    """
    Проверяет, что пароль не является слишком широко распространенным.
    """

    def validate(self, password: str, user=None) -> None:
        """
        Проверяет пароль на соответствие списку слишком широко распространенных паролей.

        :param password: Пароль, который нужно проверить.
        :param user: Пользователь, для которого пароль предназначен.
        :raises ValidationError: Если пароль слишком широко распространен.
        """
        if password.lower().strip() in self.passwords:
            raise ValidationError(
                _("Этот пароль слишком широко распространён."),
                code="password_too_common",
            )

    def get_help_text(self) -> str:
        """
        Возвращает текст, который может помочь пользователю в выборе пароля.

        :return: Текст, который может помочь пользователю в выборе пароля.
        """
        return _("Ваш пароль не может быть слишком широко распространённым.")


class CustomNumericPasswordValidator(NumericPasswordValidator):
    """
    Проверяет, что пароль не состоит только из цифр.
    """

    def validate(self, password: str, user=None) -> None:
        """
        Проверяет пароль на соответствие условию, что он не состоит только из цифр.

        :param password: Пароль, который нужно проверить.
        :param user: Пользователь, для которого пароль предназначен.
        :raises ValidationError: Если пароль состоит только из цифр.
        """
        if password.isdigit():
            raise ValidationError(
                _("Этот пароль состоит только из цифр."),
                code="password_entirely_numeric",
            )

    def get_help_text(self) -> str:
        """
        Возвращает текст, который может помочь пользователю в выборе пароля.

        :return: Текст, который может помочь пользователю в выборе пароля.
        """
        return _("Ваш пароль не может состоять только из цифр.")


class CustomUserAttributeSimilarityValidator(UserAttributeSimilarityValidator):
    """
    Проверяет, что пароль не слишком похож на другие личные данные пользователя.
    """

    def get_help_text(self) -> str:
        """
        Возвращает текст, который может помочь пользователю в выборе пароля.

        :return: Текст, который может помочь пользователю в выборе пароля.
        """
        return _(
            "Ваш пароль не должен быть слишком похож на другую вашу личную информацию."
        )
