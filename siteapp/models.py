# siteapp/models.py
import typing
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.utils import timezone
from django.conf import settings
from django.template.defaultfilters import slugify
from django.core.validators import RegexValidator
from django.core.validators import MaxValueValidator, MinValueValidator
from typing import Optional

FRONTEND_BASE_URL = getattr(settings, "FRONTEND_BASE_URL", "http://localhost:5173")


class Region(models.Model):
    """
    Представляет регион.
    """
    name = models.CharField(_("название региона"), max_length=100, unique=True)

    class Meta:
        verbose_name = _("регион")
        verbose_name_plural = _("регионы")
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Role(models.Model):
    """
    Представляет роль пользователя и её права.
    """
    name = models.CharField(_("название роли"), max_length=50, unique=True)
    can_create_article = models.BooleanField(_("может создавать статьи"), default=False)
    can_edit_own_article = models.BooleanField(
        _("может редактировать свои статьи"), default=False
    )
    can_edit_any_article = models.BooleanField(
        _("может редактировать любые статьи"), default=False
    )
    can_delete_own_article = models.BooleanField(
        _("может удалять свои статьи"), default=False
    )
    can_delete_any_article = models.BooleanField(
        _("может удалять любые статьи"), default=False
    )
    can_edit_own_comment = models.BooleanField(
        _("может редактировать свои комментарии"), default=True
    )
    can_delete_own_comment = models.BooleanField(
        _("может удалять свои комментарии"), default=True
    )
    can_delete_any_comment = models.BooleanField(
        _("может удалять любые комментарии (модерация)"), default=False
    )
    can_create_advertisement = models.BooleanField(
        _("может создавать объявления"), default=True
    )
    can_edit_own_advertisement = models.BooleanField(
        _("может редактировать свои объявления"), default=True
    )
    can_delete_own_advertisement = models.BooleanField(
        _("может удалять свои объявления"), default=True
    )
    can_manage_any_advertisement = models.BooleanField(
        _("может управлять любыми объявлениями (модерация)"), default=False
    )

    class Meta:
        verbose_name = _("роль")
        verbose_name_plural = _("роли")
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class User(AbstractUser):
    """
    Пользовательская модель, расширяющая стандартную.
    """
    display_name = models.CharField(_("отображаемое имя"), max_length=150, blank=True)
    email = models.EmailField(_("email"), unique=True)
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message=_("Номер телефона должен быть введен в формате: '+999999999'. До 15 цифр.")
    )
    phone_number = models.CharField(
        _("номер телефона"), 
        validators=[phone_regex],
        max_length=20, 
        blank=True, 
        null=True
    )

    role = models.ForeignKey(
        Role, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("роль")
    )
    region = models.ForeignKey(
        Region,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("регион"),
    )
    avatar = models.ImageField(
        _("аватар"),
        upload_to="user_avatars/",
        null=True,
        blank=True,
        help_text=_("Аватар пользователя"),
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    class Meta:
        verbose_name = _("пользователь")
        verbose_name_plural = _("пользователи")
        ordering = ["email"]

    def __str__(self) -> str:
        return self.email

    def get_full_name(self) -> str:
        """
        Возвращает полное имя пользователя.
        """
        return self.display_name or self.username

    @property
    def avatar_url(self) -> Optional[str]:
        """
        Возвращает URL аватара пользователя.
        """
        if self.avatar and hasattr(self.avatar, "url"):
            return self.avatar.url
        return None


class AdStatus(models.Model):
    """
    Представляет статус объявления.
    """
    name = models.CharField(_("название статуса"), max_length=50, unique=True)

    class Meta:
        verbose_name = _("статус объявления")
        verbose_name_plural = _("статусы объявлений")
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Species(models.Model):
    """
    Представляет вид животного.
    """
    name = models.CharField(_("название вида"), max_length=100, unique=True)

    class Meta:
        verbose_name = _("вид животного")
        verbose_name_plural = _("виды животных")
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Breed(models.Model):
    """
    Представляет породу животного.
    """
    name = models.CharField(_("название породы"), max_length=100)
    species = models.ForeignKey(
        Species, on_delete=models.CASCADE, verbose_name=_("вид")
    )

    class Meta:
        verbose_name = _("порода")
        verbose_name_plural = _("породы")
        unique_together = ("name", "species")
        ordering = ["species", "name"]

    def __str__(self) -> str:
        return f"{self.name} ({self.species.name})"


class AnimalColor(models.Model):
    """
    Представляет окрас животного.
    """
    name = models.CharField(_("название окраса"), max_length=100, unique=True)

    class Meta:
        verbose_name = _("окрас животного")
        verbose_name_plural = _("окрасы животных")
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Animal(models.Model):
    """
    Представляет животное.
    """
    GENDER_MALE = "M"
    GENDER_FEMALE = "F"
    GENDER_UNKNOWN = "U"
    GENDER_CHOICES = [
        (GENDER_MALE, _("Мальчик")),
        (GENDER_FEMALE, _("Девочка")),
        (GENDER_UNKNOWN, _("Не указан")),
    ]

    name = models.CharField(
        _("имя/кличка"),
        max_length=100,
        blank=True,
        null=True,
        help_text=_("Может быть пустым, если неизвестно"),
    )
    birth_date = models.DateField(
        _("дата рождения"),
        blank=True,
        null=True,
        help_text=_("Примерная, если точная неизвестна"),
    )
    species = models.ForeignKey(
        Species, on_delete=models.PROTECT, verbose_name=_("вид")
    )
    breed = models.ForeignKey(
        Breed,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("порода"),
        help_text=_("Может быть пустым для беспородных или если порода неизвестна"),
    )
    color = models.ForeignKey(
        AnimalColor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("окрас"),
    )
    gender = models.CharField(
        _("пол"),
        max_length=1,
        choices=GENDER_CHOICES,
        null=False,
        default=GENDER_UNKNOWN,
    )
    shelters = models.ManyToManyField(
        'Shelter',
        through='AnimalInShelter',
        related_name='animals_in_shelter',
        verbose_name=_("приюты, в которых состоит")
    )

    class Meta:
        verbose_name = _("животное")
        verbose_name_plural = _("животные")
        ordering = ["species", "name"]

    def __str__(self) -> str:
        return f"{self.name or _('Неизвестное животное')} ({self.species.name})"

    def get_gender_display_for_api(self) -> Optional[str]:
        """
        Возвращает отображаемое значение пола для API.
        """
        return self.get_gender_display() if self.gender else None


class Shelter(models.Model):
    """
    Представляет приют для животных.
    """
    name = models.CharField(_("название приюта"), max_length=200)
    address = models.CharField(_("адрес"), max_length=255)
    contacts = models.TextField(_("контакты"), blank=True)
    region = models.ForeignKey(Region, on_delete=models.PROTECT, verbose_name=_("регион"))
    website = models.URLField(_("веб-сайт приюта"), max_length=300, blank=True, null=True)

    animals = models.ManyToManyField(
        Animal,
        through='AnimalInShelter',
        verbose_name=_("животные в приюте"),
        blank=True
    )

    class Meta:
        verbose_name = _("приют")
        verbose_name_plural = _("приюты")
        ordering = ['name']

    def __str__(self) -> str:
        return self.name


class AnimalInShelter(models.Model):
    """
    Представляет животное, которое находится в приюте.

    Fields:
        animal: связь с моделью Animal, представляющей животное.
        shelter: связь с моделью Shelter, представляющей приют.
        date_admitted: дата, когда животное поступило в приют.
    """

    animal = models.ForeignKey(
        Animal,
        on_delete=models.CASCADE,
        verbose_name=_("животное"),
    )
    shelter = models.ForeignKey(
        Shelter,
        on_delete=models.CASCADE,
        verbose_name=_("приют"),
    )
    date_admitted = models.DateField(
        _("дата поступления"),
        auto_now_add=True,
        null=True,
        blank=True,
        help_text=_("Дата, когда животное поступило в приют"),
    )

    class Meta:
        verbose_name = _("животное в приюте")
        verbose_name_plural = _("животные в приютах")
        unique_together = ("animal", "shelter")
        ordering = ["shelter", "animal", "-date_admitted"]

    def __str__(self) -> str:
        """
        Возвращает строковое представление объекта.

        Returns:
            str: строковое представление объекта
        """
        return f"{self.animal} в {self.shelter} (с {self.date_admitted or 'неизвестной даты'})"


class ActiveAdvertisementManager(models.Manager):
    """
    Менеджер для получения активных объявлений.
    """

    def get_queryset(self) -> models.QuerySet:
        """
        Возвращает базовый QuerySet для объявлений.
        
        Returns:
            models.QuerySet: Базовый QuerySet.
        """
        return super().get_queryset()

    def active(self) -> models.QuerySet:
        """
        Возвращает только объявления со статусом "Активно".
        
        Returns:
            models.QuerySet: QuerySet с активными объявлениями.
        """
        try:
            active_status_name = "Активно"
            return self.get_queryset().filter(status__name=active_status_name)
        except AdStatus.DoesNotExist:
            print(
                f"WARNING: Статус '{active_status_name}' не найден, ActiveAdvertisementManager.active() вернет пустой QuerySet если status__name используется напрямую."
            )
            return self.get_queryset().none()
        except Exception as e:
            print(f"Ошибка в ActiveAdvertisementManager.active(): {e}")
            return self.get_queryset().none()

    def recently_published(self, days: int = 7) -> models.QuerySet:
        """
        Возвращает активные объявления, опубликованные за последние N дней.
        
        Args:
            days (int): Количество дней для фильтрации объявлений.

        Returns:
            models.QuerySet: QuerySet с активными объявлениями за последние N дней.
        """
        return self.active().filter(
            publication_date__gte=timezone.now() - timezone.timedelta(days=days)
        )


class Advertisement(models.Model):
    """
    Модель объявления.
    
    Attributes:
        user (models.ForeignKey): Пользователь, разместивший объявление.
        animal (models.ForeignKey): Животное, описанное в объявлении.
        status (models.ForeignKey): Статус объявления.
        title (models.CharField): Заголовок объявления.
        description (models.TextField): Описание объявления.
        publication_date (models.DateTimeField): Дата размещения объявления.
        latitude (models.FloatField): Широта, если указана.
        longitude (models.FloatField): Долгота, если указана.
    """

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name=_("пользователь")
    )
    animal = models.ForeignKey(
        Animal, on_delete=models.CASCADE, verbose_name=_("животное")
    )
    status = models.ForeignKey(
        AdStatus, on_delete=models.PROTECT, verbose_name=_("статус")
    )
    title = models.CharField(
        _("заголовок объявления"), max_length=200, default="Потеряно/Найдено животное"
    )
    description = models.TextField(_("описание"))
    publication_date = models.DateTimeField(_("дата размещения"), auto_now_add=True)
    latitude = models.FloatField(_("широта"), blank=True, null=True)
    longitude = models.FloatField(_("долгота"), blank=True, null=True)

    objects = models.Manager()
    active_ads = ActiveAdvertisementManager()

    class Meta:
        verbose_name = _("объявление")
        verbose_name_plural = _("объявления")
        ordering = ["-publication_date"]

    def __str__(self) -> str:
        """
        Возвращает строковое представление объекта.
        """
        return f"{self.title} ({self.animal.name or _('животное')}, {_('статус')}: {self.status.name})"

    def get_absolute_url(self) -> str:
        """
        Возвращает URL для просмотра этого объявления на фронтенде.
        """
        return f"{FRONTEND_BASE_URL}advertisement/{self.pk}"

class AdvertisementRating(models.Model):
    """
    Модель оценки объявления.
    
    Attributes:
        advertisement (models.ForeignKey): Объявление, которое было оценено.
        user (models.ForeignKey): Пользователь, который оставил оценку.
        rating (models.PositiveSmallIntegerField): Оценка, которую пользователь оставил.
        created_at (models.DateTimeField): Дата, когда была оставлена оценка.
    """

    advertisement = models.ForeignKey(
        Advertisement, 
        related_name='ratings', 
        on_delete=models.CASCADE,
        verbose_name=_("объявление"),
        help_text=_("Объявление, которое было оценено.")
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='ad_ratings_given',
        on_delete=models.CASCADE,
        verbose_name=_("пользователь"),
        help_text=_("Пользователь, который оставил оценку.")
    )
    rating = models.PositiveSmallIntegerField(
        _("оценка"),
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text=_("Оценка, которую пользователь оставил.")
    )
    created_at = models.DateTimeField(
        _("дата оценки"), 
        auto_now_add=True,
        help_text=_("Дата, когда была оставлена оценка.")
    )

    class Meta:
        """
        Метаданные модели.
        """
        verbose_name = _("оценка объявления")
        verbose_name_plural = _("оценки объявлений")
        unique_together = ('advertisement', 'user')
        ordering = ['-created_at']

    def __str__(self) -> str:
        """
        Возвращает строковое представление объекта.
        """
        return f"{self.rating}* от {self.user.username} для {self.advertisement.title[:20]}..."

class AdPhoto(models.Model):
    """
    Модель фотографии к объявлению.

    Attributes:
        advertisement (models.ForeignKey): Объявление, к которому привязана фотография.
        image (models.ImageField): Фотография.
    """

    advertisement = models.ForeignKey(
        Advertisement,
        related_name="photos",
        on_delete=models.CASCADE,
        verbose_name=_("объявление"),
    )
    image = models.ImageField(_("фото"), upload_to="ad_photos/%Y/%m/%d/")

    class Meta:
        """Метаданные модели."""
        verbose_name = _("фото объявления")
        verbose_name_plural = _("фото объявлений")
        ordering = ["advertisement"]

    def __str__(self) -> str:
        """Возвращает строковое представление объекта."""
        return f"{_('Фото для объявления ID')}: {self.advertisement.id}"

    @property
    def image_url(self) -> str | None:
        """
        Возвращает URL фотографии, если она есть.

        Returns:
            str | None: URL фотографии, если она есть, иначе None.
        """
        if self.image and hasattr(self.image, "url"):
            return self.image.url
        return None


class AdResponse(models.Model):
    """
    Модель отклика на объявление.

    Attributes:
        advertisement (models.ForeignKey): Объявление, к которому привязан отклик.
        user (models.ForeignKey): Пользователь, оставивший отклик.
        message (models.TextField): Сообщение отклика.
        date_created (models.DateTimeField): Дата создания отклика.
    """

    advertisement = models.ForeignKey(
        Advertisement,
        related_name="responses",
        on_delete=models.CASCADE,
        verbose_name=_("объявление"),
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name=_("пользователь")
    )
    message = models.TextField(_("сообщение"), help_text=_("Текст отклика"))
    date_created = models.DateTimeField(_("дата отклика"), auto_now_add=True)

    class Meta:
        """Метаданные модели."""
        verbose_name = _("отклик на объявление")
        verbose_name_plural = _("отклики на объявления")
        ordering = ["-date_created"]

    def __str__(self) -> str:
        """Возвращает строковое представление объекта."""
        return f"{_('Отклик от')} {self.user.get_full_name()} {_('на объявление ID')}: {self.advertisement.id}"


class ArticleCategory(models.Model):
    """
    Модель категории статей.

    Attributes:
        name (models.CharField): Название категории.
        slug (models.SlugField): Слаг категории.
    """

    name = models.CharField(_("название категории"), max_length=100, unique=True)
    slug = models.SlugField(
        _("слаг"),
        max_length=100,
        unique=True,
        blank=True,
        help_text=_(
            "Используется в URL. Оставьте пустым для автоматической генерации (на латинице)."
        ),
    )

    class Meta:
        """Метаданные модели."""
        verbose_name = _("категория статей")
        verbose_name_plural = _("категории статей")
        ordering = ["name"]

    def __str__(self) -> str:
        """Возвращает строковое представление объекта."""
        return self.name

    def save(self, *args, **kwargs) -> None:
        """
        Сохраняет объект.

        Если слаг не указан, то он будет сгенерирован автоматически на основе названия категории.
        """
        if not self.slug:
            self.slug = slugify(self.name)
            if not self.slug:
                self.slug = str(self.id) if self.id else "category"
        super().save(*args, **kwargs)


class Article(models.Model):
    """
    Модель, представляющая статью.

    Attributes:
        title (CharField): Заголовок статьи.
        content (TextField): Содержимое статьи.
        publication_date (DateTimeField): Дата публикации.
        author (ForeignKey): Автор статьи.
        main_image (ImageField): Главное изображение статьи.
        categories (ManyToManyField): Категории, к которым относится статья.
    """

    title: models.CharField = models.CharField(_("заголовок статьи"), max_length=255)
    content: models.TextField = models.TextField(_("содержимое"))
    publication_date: models.DateTimeField = models.DateTimeField(
        _("дата публикации"), auto_now_add=True
    )
    author: models.ForeignKey = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("автор"),
        limit_choices_to={"is_staff": True},
    )
    main_image: models.ImageField = models.ImageField(
        _("главное изображение"),
        upload_to="article_images/%Y/%m/%d/",
        blank=True,
        null=True,
        help_text=_(
            "Главное изображение для статьи, отображаемое в превью и на странице статьи."
        ),
    )
    categories: models.ManyToManyField = models.ManyToManyField(
        ArticleCategory,
        related_name="articles",
        blank=True,
        verbose_name=_("категории"),
    )

    class Meta:
        """
        Метаданные модели.
        """
        verbose_name = _("статья")
        verbose_name_plural = _("статьи")
        ordering = ["-publication_date"]

    def __str__(self) -> str:
        """
        Возвращает строковое представление объекта.
        """
        return self.title

    @property
    def main_image_url(self) -> typing.Optional[str]:
        """
        Возвращает URL главного изображения, если оно есть.
        """
        if self.main_image and hasattr(self.main_image, "url"):
            return self.main_image.url
        return None

    @property
    def excerpt(self) -> str:
        """
        Возвращает краткое описание статьи (150 символов).
        """
        if self.content:
            return (
                (self.content[:150] + "...")
                if len(self.content) > 150
                else self.content
            )
        return ""

    def get_absolute_url(self) -> str:
        """
        Возвращает URL для просмотра этой статьи на фронтенде.
        """
        return f"{FRONTEND_BASE_URL}article/{self.pk}"


class Comment(models.Model):
    """
    Модель комментария к статье.
    """

    article = models.ForeignKey(
        Article,
        related_name="comments",
        on_delete=models.CASCADE,
        verbose_name=_("статья"),
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name=_("пользователь")
    )
    text = models.TextField(_("текст комментария"))
    date_created = models.DateTimeField(_("дата комментария"), auto_now_add=True)

    class Meta:
        """
        Метаданные модели.
        """

        verbose_name = _("комментарий")
        verbose_name_plural = _("комментарии")
        ordering = ["-date_created"]

    def __str__(self) -> str:
        """
        Возвращает строковое представление объекта.
        """
        return f"{_('Комментарий от')} {self.user.get_full_name()} {_('к статье')}: \"{self.article.title[:30]}...\""


class Volunteering(models.Model):
    """
    Модель волонтёрства.

    Attributes:
        user (ForeignKey): Пользователь-волонтёр.
        shelter (ForeignKey): Приют, в котором происходит волонтёрство.
        start_date (DateTimeField): Дата и время начала волонтёрства.
        end_date (DateTimeField): Дата и время окончания волонтёрства.
        notes (TextField): Примечания к записи о волонтёрстве.
    """

    user: models.ForeignKey = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name=_("волонтёр")
    )
    shelter: models.ForeignKey = models.ForeignKey(
        Shelter, on_delete=models.CASCADE, verbose_name=_("приют")
    )
    start_date: models.DateTimeField = models.DateTimeField(_("дата и время начала"))
    end_date: models.DateTimeField = models.DateTimeField(
        _("дата и время окончания"), null=True, blank=True
    )
    notes: models.TextField = models.TextField(_("примечания"), blank=True)

    class Meta:
        """
        Метаданные модели.
        """

        verbose_name = _("волонтёрство")
        verbose_name_plural = _("записи о волонтёрстве")
        ordering = ["-start_date"]
        unique_together = ("user", "shelter", "start_date")

    def __str__(self) -> str:
        """
        Возвращает строковое представление объекта.

        Returns:
            str: строковое представление объекта волонтёрства.
        """
        return f"{_('Волонтёрство:')} {self.user.get_full_name()} {_('в приюте')} {self.shelter.name} {_('с')} {self.start_date.strftime('%Y-%m-%d %H:%M')}"

