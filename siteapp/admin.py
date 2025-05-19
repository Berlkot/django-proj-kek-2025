# siteapp/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from .models import (
    Region, Role, User, AdStatus, Species, Breed, Animal, Shelter,
    AnimalInShelter, Advertisement, AdPhoto, AdResponse, Article, Comment, Volunteering,
    ArticleCategory, AnimalColor, AnimalGender
)
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)

# Custom User Admin
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'username', 'display_name', 'role', 'region', 'phone_number', 'is_staff', 'is_active', 'avatar_preview_list')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups', 'role', 'region')
    search_fields = ('email', 'username', 'display_name')
    ordering = ('email',)
    raw_id_fields = ('role', 'region') # If many roles/regions
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('username', 'display_name', 'first_name', 'last_name', 'phone_number', 'avatar', 'avatar_preview_admin')}), # Added phone_number
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
        (_('Custom Fields'), {'fields': ('role', 'region')}),
    )
    readonly_fields = BaseUserAdmin.readonly_fields + ('avatar_preview_admin',)

    @admin.display(description=_("Аватар (форма)"))
    def avatar_preview_admin(self, obj):
        if obj.avatar:
            return format_html('<img src="{}" style="max-height: 100px; max-width: 100px;" />', obj.avatar.url)
        return _("Нет аватара")

    @admin.display(description=_("Аватар"))
    def avatar_preview_list(self, obj):
        if obj.avatar:
            return format_html('<img src="{}" style="max-height: 40px; max-width: 40px; border-radius: 50%;" />', obj.avatar.url)
        return _("Нет")

admin.site.register(User, UserAdmin)


@admin.register(AdStatus)
class AdStatusAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)

@admin.register(Species)
class SpeciesAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)

@admin.register(Breed)
class BreedAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'species')
    list_filter = ('species',)
    search_fields = ('name', 'species__name')
    raw_id_fields = ('species',) # Good practice if many species

# Inlines for Animal
class AnimalInShelterInline(admin.TabularInline): # Or StackedInline
    model = AnimalInShelter
    extra = 1
    raw_id_fields = ('shelter',) # Assuming many shelters
    verbose_name = _("пребывание в приюте")
    verbose_name_plural = _("пребывания в приютах")

@admin.register(AnimalColor)
class AnimalColorAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)

@admin.register(AnimalGender)
class AnimalGenderAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)

@admin.register(Animal)
class AnimalAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'species', 'breed', 'color', 'gender', 'birth_date') # Добавлены color, gender
    list_filter = ('species', 'breed', 'color', 'gender') # Добавлены color, gender
    search_fields = ('name', 'species__name', 'breed__name', 'color__name', 'gender__name')
    raw_id_fields = ('species', 'breed', 'color', 'gender') # Добавлены color, gender
    inlines = [AnimalInShelterInline]
    date_hierarchy = 'birth_date'

# Inlines for Shelter
class VolunteeringForShelterInline(admin.TabularInline):
    model = Volunteering
    extra = 1
    raw_id_fields = ('user',)
    fields = ('user', 'start_date', 'end_date', 'notes')
    verbose_name = _("волонтёрство в этом приюте")
    verbose_name_plural = _("волонтёрства в этом приюте")

class AnimalInShelterForShelterInline(admin.TabularInline):
    model = AnimalInShelter
    extra = 1
    raw_id_fields = ('animal',)
    verbose_name = _("животное в этом приюте")
    verbose_name_plural = _("животные в этом приюте")


@admin.register(Shelter)
class ShelterAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'region', 'address', 'active_animals_count')
    list_filter = ('region',)
    search_fields = ('name', 'address', 'region__name')
    raw_id_fields = ('region',)
    inlines = [AnimalInShelterForShelterInline, VolunteeringForShelterInline]

    @admin.display(description=_("Кол-во животных"))
    def active_animals_count(self, obj):
        # Example of a custom method in list_display
        return obj.animalinshelter_set.count() # Counts related AnimalInShelter objects

@admin.register(AnimalInShelter)
class AnimalInShelterAdmin(admin.ModelAdmin):
    list_display = ('animal', 'shelter', 'date_admitted')
    list_filter = ('shelter', 'date_admitted')
    search_fields = ('animal__name', 'shelter__name')
    raw_id_fields = ('animal', 'shelter')
    date_hierarchy = 'date_admitted'

# Inlines for Advertisement
class AdPhotoInline(admin.TabularInline):
    model = AdPhoto
    extra = 1
    readonly_fields = ('image_preview',)

    @admin.display(description=_("Превью"))
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 100px; max-width: 100px;" />', obj.image.url)
        return _("Нет фото")
    image_preview.allow_tags = True # For older Django versions, not needed for Django 3.2+ with format_html

class AdResponseInline(admin.StackedInline): # Or TabularInline
    model = AdResponse
    extra = 0 # Don't show empty forms by default
    readonly_fields = ('user', 'message', 'date_created')
    can_delete = False # Usually, responses shouldn't be deleted from ad page
    raw_id_fields = ('user',)

@admin.register(Advertisement)
class AdvertisementAdmin(admin.ModelAdmin):
    list_display = ('id', 'title_with_animal', 'user_email', 'status', 'publication_date_formatted', 'region_of_ad')
    list_display_links = ('id', 'title_with_animal')
    list_filter = ('status', 'publication_date', 'animal__species', 'user__region') # Filter by animal species, user region
    search_fields = ('title', 'description', 'animal__name', 'user__email', 'user__username')
    raw_id_fields = ('user', 'animal', 'status')
    date_hierarchy = 'publication_date'
    inlines = [AdPhotoInline, AdResponseInline]
    readonly_fields = ('publication_date',) # Set by auto_now_add

    @admin.display(description=_("Заголовок (Животное)"), ordering='title')
    def title_with_animal(self, obj):
        animal_name = obj.animal.name or _("Неизвестное")
        return f"{obj.title} ({animal_name} - {obj.animal.species.name})"

    @admin.display(description=_("Email пользователя"), ordering='user__email')
    def user_email(self, obj):
        return obj.user.email

    @admin.display(description=_("Дата публикации"), ordering='publication_date')
    def publication_date_formatted(self, obj):
        return obj.publication_date.strftime("%d.%m.%Y %H:%M")

    @admin.display(description=_("Регион объявления"), ordering='user__region__name')
    def region_of_ad(self, obj):
        # Assuming region of ad is based on user's region.
        # If ad has its own region, use that.
        return obj.user.region.name if obj.user.region else _("Не указан")

@admin.register(AdPhoto)
class AdPhotoAdmin(admin.ModelAdmin):
    list_display = ('id', 'advertisement_link', 'image_preview_list', 'image')
    list_select_related = ('advertisement', 'advertisement__animal') # Optimize queries
    search_fields = ('advertisement__title', 'advertisement__animal__name')
    raw_id_fields = ('advertisement',)

    @admin.display(description=_("Объявление"))
    def advertisement_link(self, obj):
        from django.urls import reverse
        link = reverse("admin:siteapp_advertisement_change", args=[obj.advertisement.id])
        return format_html('<a href="{}">{}</a>', link, str(obj.advertisement))

    @admin.display(description=_("Превью"))
    def image_preview_list(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 50px; max-width: 50px;" />', obj.image.url)
        return _("Нет фото")

@admin.register(AdResponse)
class AdResponseAdmin(admin.ModelAdmin):
    list_display = ('id', 'advertisement_link', 'user_email', 'short_message', 'date_created')
    list_filter = ('date_created', 'advertisement__status')
    search_fields = ('message', 'user__email', 'user__username', 'advertisement__title')
    raw_id_fields = ('advertisement', 'user')
    date_hierarchy = 'date_created'
    readonly_fields = ('date_created',)

    @admin.display(description=_("Объявление"))
    def advertisement_link(self, obj):
        from django.urls import reverse
        link = reverse("admin:siteapp_advertisement_change", args=[obj.advertisement.id])
        return format_html('<a href="{}">{}</a>', link, str(obj.advertisement))

    @admin.display(description=_("Email пользователя"), ordering='user__email')
    def user_email(self, obj):
        return obj.user.email

    @admin.display(description=_("Сообщение (кратко)"), ordering='message')
    def short_message(self, obj):
        return (obj.message[:75] + '...') if len(obj.message) > 75 else obj.message

# Inlines for Article
class CommentInline(admin.TabularInline): # Or StackedInline
    model = Comment
    extra = 0
    fields = ('user', 'text', 'date_created')
    readonly_fields = ('date_created',)
    raw_id_fields = ('user',)


@admin.register(ArticleCategory)
class ArticleCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)} # Автозаполнение слага на основе имени

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'author_email', 'publication_date_formatted', 'comment_count', 'image_preview_list', 'list_categories')
    list_filter = ('publication_date', 'author', 'categories') # ДОБАВЛЕН фильтр по категориям
    search_fields = ('title', 'content', 'author__email', 'author__username')
    raw_id_fields = ('author',)
    date_hierarchy = 'publication_date'
    inlines = [CommentInline]
    readonly_fields = ('publication_date', 'image_preview_admin')
    # Используем filter_horizontal для удобного выбора ManyToMany категорий
    filter_horizontal = ('categories',)
    fields = ('title', 'author', 'categories', 'content', 'main_image', 'image_preview_admin', 'publication_date')
    # prepopulated_fields = {"slug": ("title",)} # Если у статьи есть slug

    @admin.display(description=_("Категории"))
    def list_categories(self, obj):
        return ", ".join([c.name for c in obj.categories.all()])

    @admin.display(description=_("Email автора"), ordering='author__email')
    def author_email(self, obj):
        return obj.author.email if obj.author else _("Нет автора")

    @admin.display(description=_("Дата публикации"), ordering='publication_date')
    def publication_date_formatted(self, obj):
        return obj.publication_date.strftime("%d.%m.%Y %H:%M")

    @admin.display(description=_("Кол-во комментариев"))
    def comment_count(self, obj):
        return obj.comments.count()

    @admin.display(description=_("Превью изображения"))
    def image_preview_admin(self, obj):
        if obj.main_image:
            return format_html('<img src="{}" style="max-height: 200px; max-width: 200px;" />', obj.main_image.url)
        return _("Нет изображения")

    @admin.display(description=_("Превью (список)"))
    def image_preview_list(self, obj):
        if obj.main_image:
            return format_html('<img src="{}" style="max-height: 50px; max-width: 50px;" />', obj.main_image.url)
        return _("Нет изобр.")

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'article_link', 'user_email', 'short_text', 'date_created')
    list_filter = ('date_created', 'article__title')
    search_fields = ('text', 'user__email', 'user__username', 'article__title')
    raw_id_fields = ('article', 'user')
    date_hierarchy = 'date_created'
    readonly_fields = ('date_created',)

    @admin.display(description=_("Статья"), ordering='article__title')
    def article_link(self, obj):
        from django.urls import reverse
        link = reverse("admin:siteapp_article_change", args=[obj.article.id])
        return format_html('<a href="{}">{}</a>', link, str(obj.article))

    @admin.display(description=_("Email пользователя"), ordering='user__email')
    def user_email(self, obj):
        return obj.user.email

    @admin.display(description=_("Текст (кратко)"), ordering='text')
    def short_text(self, obj):
        return (obj.text[:75] + '...') if len(obj.text) > 75 else obj.text

@admin.register(Volunteering)
class VolunteeringAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_email', 'shelter_name', 'start_date_formatted', 'end_date_formatted')
    list_filter = ('start_date', 'shelter', 'user__region') # Filter by user's region
    search_fields = ('user__email', 'user__username', 'shelter__name', 'notes')
    raw_id_fields = ('user', 'shelter')
    date_hierarchy = 'start_date'

    @admin.display(description=_("Email волонтёра"), ordering='user__email')
    def user_email(self, obj):
        return obj.user.email

    @admin.display(description=_("Приют"), ordering='shelter__name')
    def shelter_name(self, obj):
        return obj.shelter.name

    @admin.display(description=_("Дата начала"), ordering='start_date')
    def start_date_formatted(self, obj):
        return obj.start_date.strftime("%d.%m.%Y %H:%M")

    @admin.display(description=_("Дата окончания"), ordering='end_date')
    def end_date_formatted(self, obj):
        return obj.end_date.strftime("%d.%m.%Y %H:%M") if obj.end_date else _("Активно")