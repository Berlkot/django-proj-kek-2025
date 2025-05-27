# siteapp/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.utils import timezone
from django.conf import settings
from django.template.defaultfilters import slugify


FRONTEND_BASE_URL = getattr(settings, "FRONTEND_BASE_URL", "http://localhost:5173")


class Region(models.Model):
    name = models.CharField(_("название региона"), max_length=100, unique=True)

    class Meta:
        verbose_name = _("регион")
        verbose_name_plural = _("регионы")
        ordering = ["name"]

    def __str__(self):
        return self.name


class Role(models.Model):
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

    def __str__(self):
        return self.name


class User(AbstractUser):

    display_name = models.CharField(_("отображаемое имя"), max_length=150, blank=True)
    email = models.EmailField(_("email"), unique=True)
    phone_number = models.CharField(
        _("номер телефона"), max_length=20, blank=True, null=True
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

    def __str__(self):
        return self.email

    def get_full_name(self):
        return self.display_name or self.username

    @property
    def avatar_url(self):
        if self.avatar and hasattr(self.avatar, "url"):
            return self.avatar.url
        return None


class AdStatus(models.Model):
    name = models.CharField(_("название статуса"), max_length=50, unique=True)

    class Meta:
        verbose_name = _("статус объявления")
        verbose_name_plural = _("статусы объявлений")
        ordering = ["name"]

    def __str__(self):
        return self.name


class Species(models.Model):
    name = models.CharField(_("название вида"), max_length=100, unique=True)

    class Meta:
        verbose_name = _("вид животного")
        verbose_name_plural = _("виды животных")
        ordering = ["name"]

    def __str__(self):
        return self.name


class Breed(models.Model):
    name = models.CharField(_("название породы"), max_length=100)
    species = models.ForeignKey(
        Species, on_delete=models.CASCADE, verbose_name=_("вид")
    )

    class Meta:
        verbose_name = _("порода")
        verbose_name_plural = _("породы")
        unique_together = ("name", "species")
        ordering = ["species", "name"]

    def __str__(self):
        return f"{self.name} ({self.species.name})"


class AnimalColor(models.Model):
    name = models.CharField(_("название окраса"), max_length=100, unique=True)

    class Meta:
        verbose_name = _("окрас животного")
        verbose_name_plural = _("окрасы животных")
        ordering = ["name"]

    def __str__(self):
        return self.name


class Animal(models.Model):

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

    class Meta:
        verbose_name = _("животное")
        verbose_name_plural = _("животные")
        ordering = ["species", "name"]

    def __str__(self):
        return f"{self.name or _('Неизвестное животное')} ({self.species.name})"

    def get_gender_display_for_api(self):
        return self.get_gender_display() if self.gender else None


class Shelter(models.Model):
    name = models.CharField(_("название приюта"), max_length=200)
    address = models.CharField(_("адрес"), max_length=255)
    contacts = models.TextField(_("контакты"), blank=True)
    region = models.ForeignKey(
        Region, on_delete=models.PROTECT, verbose_name=_("регион")
    )
    website = models.URLField(
        _("веб-сайт приюта"), max_length=300, blank=True, null=True
    )

    class Meta:
        verbose_name = _("приют")
        verbose_name_plural = _("приюты")
        ordering = ["name"]

    def __str__(self):
        return self.name


class AnimalInShelter(models.Model):
    animal = models.ForeignKey(
        Animal, on_delete=models.CASCADE, verbose_name=_("животное")
    )
    shelter = models.ForeignKey(
        Shelter, on_delete=models.CASCADE, verbose_name=_("приют")
    )
    date_admitted = models.DateField(
        _("дата поступления"), auto_now_add=True, null=True, blank=True
    )

    class Meta:
        verbose_name = _("животное в приюте")
        verbose_name_plural = _("животные в приютах")
        unique_together = ("animal", "shelter")
        ordering = ["shelter", "animal"]

    def __str__(self):
        return f"{self.animal} в {self.shelter}"


class ActiveAdvertisementManager(models.Manager):
    def get_queryset(self):

        return super().get_queryset()

    def active(self):
        """
        Возвращает только объявления со статусом "Активно".
        """
        try:

            active_status_name = "Активно"

            return self.get_queryset().filter(status__name=active_status_name)
        except AdStatus.DoesNotExist:
            print(
                f"WARNING: Status '{active_status_name}' not found, ActiveAdvertisementManager.active() will return empty queryset if status__name is used directly."
            )
            return self.get_queryset().none()
        except Exception as e:
            print(f"Error in ActiveAdvertisementManager.active(): {e}")
            return self.get_queryset().none()

    def recently_published(self, days=7):
        """
        Возвращает активные объявления, опубликованные за последние N дней.
        """
        return self.active().filter(
            publication_date__gte=timezone.now() - timezone.timedelta(days=days)
        )


class Advertisement(models.Model):
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

    def __str__(self):
        return f"{self.title} ({self.animal.name or _('животное')}, {_('статус')}: {self.status.name})"

    def get_absolute_url(self):
        """
        Возвращает URL для просмотра этого объявления на фронтенде.
        """

        return f"{FRONTEND_BASE_URL}advertisement/{self.pk}"


class AdPhoto(models.Model):
    advertisement = models.ForeignKey(
        Advertisement,
        related_name="photos",
        on_delete=models.CASCADE,
        verbose_name=_("объявление"),
    )
    image = models.ImageField(_("фото"), upload_to="ad_photos/%Y/%m/%d/")

    class Meta:
        verbose_name = _("фото объявления")
        verbose_name_plural = _("фото объявлений")
        ordering = ["advertisement"]

    def __str__(self):
        return f"{_('Фото для объявления ID')}: {self.advertisement.id}"

    @property
    def image_url(self):
        if self.image and hasattr(self.image, "url"):
            return self.image.url
        return None


class AdResponse(models.Model):
    advertisement = models.ForeignKey(
        Advertisement,
        related_name="responses",
        on_delete=models.CASCADE,
        verbose_name=_("объявление"),
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name=_("пользователь")
    )
    message = models.TextField(_("сообщение"))
    date_created = models.DateTimeField(_("дата отклика"), auto_now_add=True)

    class Meta:
        verbose_name = _("отклик на объявление")
        verbose_name_plural = _("отклики на объявления")
        ordering = ["-date_created"]

    def __str__(self):
        return f"{_('Отклик от')} {self.user.get_full_name()} {_('на объявление ID')}: {self.advertisement.id}"


class ArticleCategory(models.Model):
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
        verbose_name = _("категория статей")
        verbose_name_plural = _("категории статей")
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:

            self.slug = slugify(self.name)
            if not self.slug:
                self.slug = str(self.id) if self.id else "category"
        super().save(*args, **kwargs)


class Article(models.Model):
    title = models.CharField(_("заголовок статьи"), max_length=255)
    content = models.TextField(_("содержимое"))
    publication_date = models.DateTimeField(_("дата публикации"), auto_now_add=True)
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("автор"),
        limit_choices_to={"is_staff": True},
    )
    main_image = models.ImageField(
        _("главное изображение"),
        upload_to="article_images/%Y/%m/%d/",
        blank=True,
        null=True,
        help_text=_(
            "Главное изображение для статьи, отображаемое в превью и на странице статьи."
        ),
    )
    categories = models.ManyToManyField(
        ArticleCategory,
        related_name="articles",
        blank=True,
        verbose_name=_("категории"),
    )

    class Meta:
        verbose_name = _("статья")
        verbose_name_plural = _("статьи")
        ordering = ["-publication_date"]

    def __str__(self):
        return self.title

    @property
    def main_image_url(self):
        if self.main_image and hasattr(self.main_image, "url"):
            return self.main_image.url
        return None

    @property
    def excerpt(self):
        if self.content:
            return (
                (self.content[:150] + "...")
                if len(self.content) > 150
                else self.content
            )
        return ""

    def get_absolute_url(self):
        """
        Возвращает URL для просмотра этой статьи на фронтенде.
        """

        return f"{FRONTEND_BASE_URL}article/{self.pk}"


class Comment(models.Model):
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
        verbose_name = _("комментарий")
        verbose_name_plural = _("комментарии")
        ordering = ["-date_created"]

    def __str__(self):
        return f"{_('Комментарий от')} {self.user.get_full_name()} {_('к статье')}: \"{self.article.title[:30]}...\""


class Volunteering(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_("волонтёр"))
    shelter = models.ForeignKey(
        Shelter, on_delete=models.CASCADE, verbose_name=_("приют")
    )
    start_date = models.DateTimeField(_("дата и время начала"))
    end_date = models.DateTimeField(_("дата и время окончания"), null=True, blank=True)
    notes = models.TextField(_("примечания"), blank=True)

    class Meta:
        verbose_name = _("волонтёрство")
        verbose_name_plural = _("записи о волонтёрстве")
        ordering = ["-start_date"]
        unique_together = ("user", "shelter", "start_date")

    def __str__(self):
        return f"{_('Волонтёрство:')} {self.user.get_full_name()} {_('в приюте')} {self.shelter.name} {_('с')} {self.start_date.strftime('%Y-%m-%d %H:%M')}"
