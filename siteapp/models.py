from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html # For admin display methods

# --- Core Entities ---

class Region(models.Model):
    name = models.CharField(_("название региона"), max_length=100, unique=True)

    class Meta:
        verbose_name = _("регион")
        verbose_name_plural = _("регионы")
        ordering = ['name']

    def __str__(self):
        return self.name

class Role(models.Model):
    name = models.CharField(_("название роли"), max_length=50, unique=True)
    can_create_article = models.BooleanField(_("может создавать статьи"), default=False)
    can_edit_own_article = models.BooleanField(_("может редактировать свои статьи"), default=False) # Если авторы - не только модеры
    can_edit_any_article = models.BooleanField(_("может редактировать любые статьи"), default=False)
    can_delete_own_article = models.BooleanField(_("может удалять свои статьи"), default=False) # Аналогично
    can_delete_any_article = models.BooleanField(_("может удалять любые статьи"), default=False)

    class Meta:
        verbose_name = _("роль")
        verbose_name_plural = _("роли")
        ordering = ['name']

    def __str__(self):
        return self.name

class User(AbstractUser):
    # Django's AbstractUser already has username, first_name, last_name, email, password, is_staff, is_active, date_joined.
    # We'll use email as the primary identifier.
    # The schema has 'имя' which could map to first_name or a new 'full_name' field.
    # Let's assume 'имя' in the schema maps to a general name field and use AbstractUser's 'username' for login.
    # If 'имя' is meant to be a display name, we can add it:
    display_name = models.CharField(_("отображаемое имя"), max_length=150, blank=True)
    email = models.EmailField(_("email"), unique=True) # Make email unique and primary identifier
    phone_number = models.CharField(_("номер телефона"), max_length=20, blank=True, null=True)
    # 'пароль_hash' is handled by Django's password management.
    role = models.ForeignKey(
        Role,
        on_delete=models.SET_NULL,
        null=True,
        blank=True, # A user might not have a specific role initially
        verbose_name=_("роль")
    )
    region = models.ForeignKey(
        Region,
        on_delete=models.SET_NULL,
        null=True,
        blank=True, # A user might not specify a region
        verbose_name=_("регион")
    )
    avatar = models.ImageField(_("аватар"), upload_to='user_avatars/', null=True, blank=True, help_text=_("Аватар пользователя"))

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = _("пользователь")
        verbose_name_plural = _("пользователи")
        ordering = ['email']

    def __str__(self):
        return self.email

    def get_full_name(self):
        return self.display_name or self.username

    @property
    def avatar_url(self):
        if self.avatar and hasattr(self.avatar, 'url'):
            return self.avatar.url
        return None # Or path to a default placeholder

class AdStatus(models.Model):
    name = models.CharField(_("название статуса"), max_length=50, unique=True)

    class Meta:
        verbose_name = _("статус объявления")
        verbose_name_plural = _("статусы объявлений")
        ordering = ['name']

    def __str__(self):
        return self.name

class Species(models.Model): # Вид
    name = models.CharField(_("название вида"), max_length=100, unique=True)

    class Meta:
        verbose_name = _("вид животного")
        verbose_name_plural = _("виды животных")
        ordering = ['name']

    def __str__(self):
        return self.name

class Breed(models.Model): # Порода
    name = models.CharField(_("название породы"), max_length=100)
    species = models.ForeignKey(Species, on_delete=models.CASCADE, verbose_name=_("вид"))

    class Meta:
        verbose_name = _("порода")
        verbose_name_plural = _("породы")
        unique_together = ('name', 'species') # A breed name should be unique within its species
        ordering = ['species', 'name']

    def __str__(self):
        return f"{self.name} ({self.species.name})"

class AnimalColor(models.Model):
    name = models.CharField(_("название окраса"), max_length=100, unique=True)

    class Meta:
        verbose_name = _("окрас животного")
        verbose_name_plural = _("окрасы животных")
        ordering = ['name']

    def __str__(self):
        return self.name

class AnimalGender(models.Model):
    name = models.CharField(_("пол"), max_length=30, unique=True) # e.g., "Мальчик", "Девочка", "Не указан"

    class Meta:
        verbose_name = _("пол животного")
        verbose_name_plural = _("пол животных")
        ordering = ['name']

    def __str__(self):
        return self.name

class Animal(models.Model):
    name = models.CharField(_("имя/кличка"), max_length=100, blank=True, null=True, help_text=_("Может быть пустым, если неизвестно"))
    birth_date = models.DateField(_("дата рождения"), blank=True, null=True, help_text=_("Примерная, если точная неизвестна"))
    species = models.ForeignKey(Species, on_delete=models.PROTECT, verbose_name=_("вид"))
    breed = models.ForeignKey(
        Breed,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("порода"),
        help_text=_("Может быть пустым для беспородных или если порода неизвестна")
    )
    color = models.ForeignKey(
        AnimalColor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("окрас")
    )
    gender = models.ForeignKey(
        AnimalGender,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("пол")
    )
    # Consider adding 'description', 'photo' fields here too (если они специфичны для животного, а не объявления)

    class Meta:
        verbose_name = _("животное")
        verbose_name_plural = _("животные")
        ordering = ['species', 'name']

    def __str__(self):
        return f"{self.name or _('Неизвестное животное')} ({self.species.name})"

class Shelter(models.Model): # Приют
    name = models.CharField(_("название приюта"), max_length=200)
    address = models.CharField(_("адрес"), max_length=255)
    contacts = models.TextField(_("контакты"), blank=True)
    region = models.ForeignKey(Region, on_delete=models.PROTECT, verbose_name=_("регион"))
    # animals = models.ManyToManyField(Animal, through='AnimalInShelter', blank=True, verbose_name=_("животные в приюте"))


    class Meta:
        verbose_name = _("приют")
        verbose_name_plural = _("приюты")
        ordering = ['name']

    def __str__(self):
        return self.name

class AnimalInShelter(models.Model):
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE, verbose_name=_("животное"))
    shelter = models.ForeignKey(Shelter, on_delete=models.CASCADE, verbose_name=_("приют"))
    date_admitted = models.DateField(_("дата поступления"), auto_now_add=True, null=True, blank=True) # Example extra field

    class Meta:
        verbose_name = _("животное в приюте")
        verbose_name_plural = _("животные в приютах")
        unique_together = ('animal', 'shelter') # An animal can be in a shelter only once
        ordering = ['shelter', 'animal']

    def __str__(self):
        return f"{self.animal} в {self.shelter}"


class Advertisement(models.Model): # Объявление
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_("пользователь"))
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE, verbose_name=_("животное"))
    status = models.ForeignKey(AdStatus, on_delete=models.PROTECT, verbose_name=_("статус"))
    title = models.CharField(_("заголовок объявления"), max_length=200, default="Потеряно/Найдено животное") # Added for better display
    description = models.TextField(_("описание"))
    publication_date = models.DateTimeField(_("дата размещения"), auto_now_add=True)
    latitude = models.FloatField(_("широта"), blank=True, null=True)
    longitude = models.FloatField(_("долгота"), blank=True, null=True)
    # is_active = models.BooleanField(_("активно"), default=True) # Consider this for soft deletes/archiving

    class Meta:
        verbose_name = _("объявление")
        verbose_name_plural = _("объявления")
        ordering = ['-publication_date']

    def __str__(self):
        return f"{self.title} ({self.animal.name or _('животное')}, {_('статус')}: {self.status.name})"

class AdPhoto(models.Model): # Объявление_Фото
    advertisement = models.ForeignKey(Advertisement, related_name='photos', on_delete=models.CASCADE, verbose_name=_("объявление"))
    image = models.ImageField(_("фото"), upload_to='ad_photos/%Y/%m/%d/') # Using ImageField
    # url = models.URLField(_("URL фото"), max_length=500) # If storing external URLs

    class Meta:
        verbose_name = _("фото объявления")
        verbose_name_plural = _("фото объявлений")
        ordering = ['advertisement']

    def __str__(self):
        return f"{_('Фото для объявления ID')}: {self.advertisement.id}"

    @property
    def image_url(self):
        if self.image and hasattr(self.image, 'url'):
            return self.image.url
        return None

class AdResponse(models.Model): # Отклик / Комментарий к объявлению
    advertisement = models.ForeignKey(Advertisement, related_name='responses', on_delete=models.CASCADE, verbose_name=_("объявление"))
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_("пользователь")) # Автор отклика/комментария
    message = models.TextField(_("сообщение"))
    date_created = models.DateTimeField(_("дата отклика"), auto_now_add=True)
    # parent_response = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies') # Для вложенных комментариев, если нужно

    class Meta:
        verbose_name = _("отклик на объявление")
        verbose_name_plural = _("отклики на объявления")
        ordering = ['-date_created'] # Сначала новые комментарии

    def __str__(self):
        return f"{_('Отклик от')} {self.user.get_full_name()} {_('на объявление ID')}: {self.advertisement.id}"

# --- Articles and Comments ---


class ArticleCategory(models.Model):
    name = models.CharField(_("название категории"), max_length=100, unique=True)
    slug = models.SlugField(_("слаг"), max_length=100, unique=True, blank=True, help_text=_("Используется в URL. Оставьте пустым для автоматической генерации (на латинице)."))

    class Meta:
        verbose_name = _("категория статей")
        verbose_name_plural = _("категории статей")
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            # Генерируем slug из name, преобразуя кириллицу в латиницу (если необходимо использовать специфичные библиотеки для транслитерации, например, pytils)
            # Стандартный slugify просто удалит не-ascii символы или заменит пробелы.
            # Для лучшей транслитерации можно использовать pytils.translit.slugify(self.name)
            self.slug = slugify(self.name)
            if not self.slug: # Если имя состоит только из символов, которые удаляются
                 self.slug = str(self.id) if self.id else 'category' # Простой фоллбэк
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
        limit_choices_to={'is_staff': True}
    )
    main_image = models.ImageField(
        _("главное изображение"),
        upload_to='article_images/%Y/%m/%d/',
        blank=True,
        null=True,
        help_text=_("Главное изображение для статьи, отображаемое в превью и на странице статьи.")
    )
    categories = models.ManyToManyField(
        ArticleCategory,
        related_name='articles',
        blank=True,
        verbose_name=_("категории")
    )
    # slug = models.SlugField(unique=True, blank=True) # Если нужен slug для самой статьи

    class Meta:
        verbose_name = _("статья")
        verbose_name_plural = _("статьи")
        ordering = ['-publication_date']

    def __str__(self):
        return self.title

    @property
    def main_image_url(self):
        if self.main_image and hasattr(self.main_image, 'url'):
            return self.main_image.url
        return None # Или URL плейсхолдера по умолчанию

    @property
    def excerpt(self):
        if self.content:
            return (self.content[:150] + '...') if len(self.content) > 150 else self.content
        return ""

class Comment(models.Model):
    article = models.ForeignKey(Article, related_name='comments', on_delete=models.CASCADE, verbose_name=_("статья"))
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_("пользователь"))
    text = models.TextField(_("текст комментария"))
    date_created = models.DateTimeField(_("дата комментария"), auto_now_add=True)
    # parent_comment = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies') # For threaded comments

    class Meta:
        verbose_name = _("комментарий")
        verbose_name_plural = _("комментарии")
        ordering = ['-date_created']

    def __str__(self):
        return f"{_('Комментарий от')} {self.user.get_full_name()} {_('к статье')}: \"{self.article.title[:30]}...\""

# --- Volunteering ---

class Volunteering(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_("волонтёр"))
    shelter = models.ForeignKey(Shelter, on_delete=models.CASCADE, verbose_name=_("приют"))
    start_date = models.DateTimeField(_("дата и время начала"))
    end_date = models.DateTimeField(_("дата и время окончания"), null=True, blank=True)
    notes = models.TextField(_("примечания"), blank=True)

    class Meta:
        verbose_name = _("волонтёрство")
        verbose_name_plural = _("записи о волонтёрстве")
        ordering = ['-start_date']
        unique_together = ('user', 'shelter', 'start_date') # Prevent duplicate entries

    def __str__(self):
        return f"{_('Волонтёрство:')} {self.user.get_full_name()} {_('в приюте')} {self.shelter.name} {_('с')} {self.start_date.strftime('%Y-%m-%d %H:%M')}"


