# siteapp/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.http import HttpResponse
import io, os
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from .models import (
    Region,
    Role,
    User,
    AdStatus,
    Species,
    Breed,
    Animal,
    Shelter,
    AnimalInShelter,
    Advertisement,
    AdPhoto,
    AdResponse,
    Article,
    Comment,
    Volunteering,
    ArticleCategory,
    AnimalColor,
)
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch, cm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Image,
    Table,
    TableStyle,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "display_article_permissions",
        "display_comment_permissions",
        "display_comment_permissions",
    )
    search_fields = ("name",)

    fieldsets = (
        (None, {"fields": ("name",)}),
        (
            "Права на статьи",
            {
                "classes": ("collapse",),
                "fields": (
                    "can_create_article",
                    "can_edit_own_article",
                    "can_edit_any_article",
                    "can_delete_own_article",
                    "can_delete_any_article",
                ),
            },
        ),
        (
            "Права на комментарии",
            {
                "classes": ("collapse",),
                "fields": (
                    "can_edit_own_comment",
                    "can_delete_own_comment",
                    "can_delete_any_comment",
                ),
            },
        ),
        (
            "Права на объявления",
            {
                "classes": ("collapse",),
                "fields": (
                    "can_create_advertisement",
                    "can_edit_own_advertisement",
                    "can_delete_own_advertisement",
                    "can_manage_any_advertisement",
                ),
            },
        ),
    )

    @admin.display(description="Права на статьи", boolean=False)
    def display_article_permissions(self, obj):
        perms = []
        if obj.can_create_article:
            perms.append("Создание")
        if obj.can_edit_own_article:
            perms.append("Ред. свои")
        if obj.can_edit_any_article:
            perms.append("Ред. все")
        if obj.can_delete_own_article:
            perms.append("Удал. свои")
        if obj.can_delete_any_article:
            perms.append("Удал. все")
        return ", ".join(perms) if perms else "Нет прав"

    @admin.display(description="Права на объявления")
    def display_advertisement_permissions(self, obj):
        perms = []
        if obj.can_create_advertisement:
            perms.append("Создание")
        if obj.can_edit_own_advertisement:
            perms.append("Ред. свои")
        if obj.can_delete_own_advertisement:
            perms.append("Удал. свои")
        if obj.can_manage_any_advertisement:
            perms.append("Упр. всеми (модерация)")
        return ", ".join(perms) if perms else "Нет спец. прав"

    @admin.display(description="Права на комментарии", boolean=False)
    def display_comment_permissions(self, obj):
        perms = []
        if obj.can_edit_own_comment:
            perms.append("Ред. свои")
        if obj.can_delete_own_comment:
            perms.append("Удал. свои")
        if obj.can_delete_any_comment:
            perms.append("Удал. все (модерация)")
        return ", ".join(perms) if perms else "Нет прав"


@admin.action(description="Проверить наличие активных объявлений у пользователей")
def check_active_ads(modeladmin, request, queryset):
    users_with_active_ads = 0
    users_without_active_ads = 0
    active_status = None
    try:
        active_status = AdStatus.objects.get(name="Активно")
    except AdStatus.DoesNotExist:
        modeladmin.message_user(request, "Статус 'Активно' не найден.", level="error")
        return

    for user in queryset:

        if Advertisement.objects.filter(user=user, status=active_status).exists():
            users_with_active_ads += 1
        else:
            users_without_active_ads += 1

    modeladmin.message_user(
        request,
        f"{users_with_active_ads} пользователей имеют активные объявления. "
        f"{users_without_active_ads} пользователей не имеют активных объявлений.",
    )


@admin.action(
    description="Деактивировать выбранных пользователей (кроме суперпользователей)"
)
def deactivate_users(modeladmin, request, queryset):

    users_to_deactivate = queryset.exclude(is_superuser=True)
    updated_count = users_to_deactivate.update(is_active=False)
    modeladmin.message_user(
        request, f"{updated_count} пользователей были деактивированы."
    )


# Custom User Admin
class UserAdmin(BaseUserAdmin):
    list_display = (
        "email",
        "username",
        "display_name",
        "role",
        "region",
        "phone_number",
        "is_staff",
        "is_active",
        "avatar_preview_list",
    )
    list_filter = ("is_staff", "is_superuser", "is_active", "groups", "role", "region")
    search_fields = ("email", "username", "display_name")
    ordering = ("email",)
    raw_id_fields = ("role", "region")
    actions = [check_active_ads, deactivate_users]
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            _("Personal info"),
            {
                "fields": (
                    "username",
                    "display_name",
                    "first_name",
                    "last_name",
                    "phone_number",
                    "avatar",
                    "avatar_preview_admin",
                )
            },
        ),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
        (_("Custom Fields"), {"fields": ("role", "region")}),
    )
    readonly_fields = BaseUserAdmin.readonly_fields + ("avatar_preview_admin",)

    @admin.display(description=_("Аватар (форма)"))
    def avatar_preview_admin(self, obj):
        if obj.avatar:
            return format_html(
                '<img src="{}" style="max-height: 100px; max-width: 100px;" />',
                obj.avatar.url,
            )
        return _("Нет аватара")

    @admin.display(description=_("Аватар"))
    def avatar_preview_list(self, obj):
        if obj.avatar:
            return format_html(
                '<img src="{}" style="max-height: 40px; max-width: 40px; border-radius: 50%;" />',
                obj.avatar.url,
            )
        return _("Нет")


admin.site.register(User, UserAdmin)


@admin.register(AdStatus)
class AdStatusAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


@admin.register(Species)
class SpeciesAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


@admin.register(Breed)
class BreedAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "species")
    list_filter = ("species",)
    search_fields = ("name", "species__name")
    raw_id_fields = ("species",)


# Inlines for Animal
class AnimalInShelterInline(admin.TabularInline):
    model = AnimalInShelter
    extra = 1
    raw_id_fields = ("shelter",)
    verbose_name = _("пребывание в приюте")
    verbose_name_plural = _("пребывания в приютах")


@admin.register(AnimalColor)
class AnimalColorAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


@admin.register(Animal)
class AnimalAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "species",
        "breed",
        "color",
        "get_gender_display",
        "birth_date",
    )
    list_filter = ("species", "breed", "color", "gender")
    search_fields = ("name", "species__name", "breed__name", "color__name", "gender")
    raw_id_fields = ("species", "breed", "color")
    inlines = [AnimalInShelterInline]
    date_hierarchy = "birth_date"


# Inlines for Shelter
class VolunteeringForShelterInline(admin.TabularInline):
    model = Volunteering
    extra = 1
    raw_id_fields = ("user",)
    fields = ("user", "start_date", "end_date", "notes")
    verbose_name = _("волонтёрство в этом приюте")
    verbose_name_plural = _("волонтёрства в этом приюте")


class AnimalInShelterForShelterInline(admin.TabularInline):
    model = AnimalInShelter
    extra = 1
    raw_id_fields = ("animal",)
    verbose_name = _("животное в этом приюте")
    verbose_name_plural = _("животные в этом приюте")


@admin.register(Shelter)
class ShelterAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "region",
        "address",
        "website_link",
        "active_animals_count",
    )
    list_filter = ("region",)
    search_fields = ("name", "address", "region__name", "website")
    raw_id_fields = ("region",)
    inlines = [AnimalInShelterForShelterInline, VolunteeringForShelterInline]

    @admin.display(description=_("Веб-сайт"))
    def website_link(self, obj):
        if obj.website:
            return format_html('<a href="{0}" target="_blank">{0}</a>', obj.website)
        return "–"

    @admin.display(description=_("Кол-во животных"))
    def active_animals_count(self, obj):
        return obj.animalinshelter_set.count()


@admin.register(AnimalInShelter)
class AnimalInShelterAdmin(admin.ModelAdmin):
    list_display = ("animal", "shelter", "date_admitted")
    list_filter = ("shelter", "date_admitted")
    search_fields = ("animal__name", "shelter__name")
    raw_id_fields = ("animal", "shelter")
    date_hierarchy = "date_admitted"


class AdPhotoInline(admin.TabularInline):
    model = AdPhoto
    extra = 1
    readonly_fields = ("image_preview",)

    @admin.display(description=_("Превью"))
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 100px; max-width: 100px;" />',
                obj.image.url,
            )
        return _("Нет фото")

    image_preview.allow_tags = True


class AdResponseInline(admin.StackedInline):
    model = AdResponse
    extra = 0
    readonly_fields = ("user", "message", "date_created")
    can_delete = False
    raw_id_fields = ("user",)


try:

    font_path_dejavu = "DejaVuSans.ttf"
    pdfmetrics.registerFont(TTFont("DejaVuSans", font_path_dejavu))
    FONT_FAMILY_RU = "DejaVuSans"
except:
    print(
        "WARNING: DejaVuSans.ttf not found. Cyrillic in PDF might not work correctly."
    )
    FONT_FAMILY_RU = "Helvetica"


def export_advertisements_to_pdf(modeladmin, request, queryset):
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="advertisements_report.pdf"'
    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=30,
        leftMargin=30,
        topMargin=30,
        bottomMargin=18,
    )

    styles = getSampleStyleSheet()

    normal_style = ParagraphStyle(name="Normal_RU", parent=styles["Normal"])
    h1_style = ParagraphStyle(name="h1_RU", parent=styles["h1"], alignment=TA_CENTER)
    h3_style = ParagraphStyle(name="h3_RU", parent=styles["h3"])
    justify_style = ParagraphStyle(
        name="Justify_RU", parent=styles["Normal"], alignment=TA_JUSTIFY
    )
    center_style = ParagraphStyle(
        name="Center_RU", parent=styles["Normal"], alignment=TA_CENTER
    )

    normal_style.fontName = FONT_FAMILY_RU
    h1_style.fontName = FONT_FAMILY_RU
    h3_style.fontName = FONT_FAMILY_RU
    justify_style.fontName = FONT_FAMILY_RU
    center_style.fontName = FONT_FAMILY_RU

    story = []
    story.append(Paragraph("Отчет по объявлениям", h1_style))
    story.append(Spacer(1, 0.5 * inch))

    for ad in queryset:
        story.append(
            Paragraph(f"<b><u>Объявление ID: {ad.id} - {ad.title}</u></b>", h3_style)
        )
        story.append(Spacer(1, 0.1 * inch))

        ad_data_text = [
            f"<b>Пользователь:</b> {ad.user.display_name or ad.user.username} ({ad.user.email})",
            f"<b>Статус:</b> {ad.status.name}",
            f"<b>Дата публикации:</b> {ad.publication_date.strftime('%d.%m.%Y %H:%M')}",
            f"<b>Животное:</b> {ad.animal.name or 'Без имени'} ({ad.animal.species.name})",
        ]
        if ad.animal.breed:
            ad_data_text.append(f"<b>Порода:</b> {ad.animal.breed.name}")

        for line in ad_data_text:
            story.append(Paragraph(line, normal_style))

        story.append(Paragraph("<b>Описание:</b>", normal_style))
        story.append(
            Paragraph(
                ad.description[:800] + ("..." if len(ad.description) > 800 else ""),
                justify_style,
            )
        )

        story.append(Spacer(1, 0.3 * inch))
        story.append(Paragraph("____________________________________", center_style))
        story.append(Spacer(1, 0.3 * inch))

    doc.build(story)
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response


export_advertisements_to_pdf.short_description = (
    "Экспортировать выбранные объявления в PDF"
)


@admin.action(description='Пометить выбранные как "Требует модерации"')
def make_needs_moderation(modeladmin, request, queryset):
    try:
        needs_moderation_status = AdStatus.objects.get(name="Требует модерации")
        updated_count = queryset.update(status=needs_moderation_status)
        modeladmin.message_user(
            request,
            f"{updated_count} объявлений были помечены как 'Требует модерации'.",
        )
    except AdStatus.DoesNotExist:
        modeladmin.message_user(
            request, "Ошибка: Статус 'Требует модерации' не найден.", level="error"
        )
    except Exception as e:
        modeladmin.message_user(request, f"Произошла ошибка: {e}", level="error")


@admin.action(description="Удалить выбранные архивные объявления")
def delete_archived_ads(modeladmin, request, queryset):

    archived_status_name = "В архиве"
    try:
        archived_status = AdStatus.objects.get(name=archived_status_name)

        ads_to_delete = queryset.filter(status=archived_status)
        deleted_count, _ = ads_to_delete.delete()
        modeladmin.message_user(
            request, f"{deleted_count} архивных объявлений были удалены."
        )
    except AdStatus.DoesNotExist:
        modeladmin.message_user(
            request, f"Статус '{archived_status_name}' не найден.", level="error"
        )
    except Exception as e:
        modeladmin.message_user(
            request, f"Произошла ошибка при удалении: {e}", level="error"
        )


@admin.register(Advertisement)
class AdvertisementAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title_with_animal",
        "user_email",
        "status",
        "publication_date_formatted",
        "region_of_ad",
    )
    list_display_links = ("id", "title_with_animal")
    list_filter = ("status", "publication_date", "animal__species", "user__region")
    search_fields = (
        "title",
        "description",
        "animal__name",
        "user__email",
        "user__username",
    )
    raw_id_fields = ("user", "animal", "status")
    date_hierarchy = "publication_date"
    inlines = [AdPhotoInline, AdResponseInline]
    actions = [export_advertisements_to_pdf, make_needs_moderation, delete_archived_ads]
    readonly_fields = ("publication_date",)

    @admin.display(description=_("Заголовок (Животное)"), ordering="title")
    def title_with_animal(self, obj):
        animal_name = obj.animal.name or _("Неизвестное")
        return f"{obj.title} ({animal_name} - {obj.animal.species.name})"

    @admin.display(description=_("Email пользователя"), ordering="user__email")
    def user_email(self, obj):
        return obj.user.email

    @admin.display(description=_("Дата публикации"), ordering="publication_date")
    def publication_date_formatted(self, obj):
        return obj.publication_date.strftime("%d.%m.%Y %H:%M")

    @admin.display(description=_("Регион объявления"), ordering="user__region__name")
    def region_of_ad(self, obj):

        return obj.user.region.name if obj.user.region else _("Не указан")


@admin.register(AdPhoto)
class AdPhotoAdmin(admin.ModelAdmin):
    list_display = ("id", "advertisement_link", "image_preview_list", "image")
    list_select_related = ("advertisement", "advertisement__animal")
    search_fields = ("advertisement__title", "advertisement__animal__name")
    raw_id_fields = ("advertisement",)

    @admin.display(description=_("Объявление"))
    def advertisement_link(self, obj):
        from django.urls import reverse

        link = reverse(
            "admin:siteapp_advertisement_change", args=[obj.advertisement.id]
        )
        return format_html('<a href="{}">{}</a>', link, str(obj.advertisement))

    @admin.display(description=_("Превью"))
    def image_preview_list(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 50px; max-width: 50px;" />',
                obj.image.url,
            )
        return _("Нет фото")


@admin.register(AdResponse)
class AdResponseAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "advertisement_link",
        "user_email",
        "short_message",
        "date_created",
    )
    list_filter = ("date_created", "advertisement__status")
    search_fields = ("message", "user__email", "user__username", "advertisement__title")
    raw_id_fields = ("advertisement", "user")
    date_hierarchy = "date_created"
    readonly_fields = ("date_created",)

    @admin.display(description=_("Объявление"))
    def advertisement_link(self, obj):
        from django.urls import reverse

        link = reverse(
            "admin:siteapp_advertisement_change", args=[obj.advertisement.id]
        )
        return format_html('<a href="{}">{}</a>', link, str(obj.advertisement))

    @admin.display(description=_("Email пользователя"), ordering="user__email")
    def user_email(self, obj):
        return obj.user.email

    @admin.display(description=_("Сообщение (кратко)"), ordering="message")
    def short_message(self, obj):
        return (obj.message[:75] + "...") if len(obj.message) > 75 else obj.message


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0
    fields = ("user", "text", "date_created")
    readonly_fields = ("date_created",)
    raw_id_fields = ("user",)


@admin.register(ArticleCategory)
class ArticleCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "author_email",
        "publication_date_formatted",
        "comment_count",
        "image_preview_list",
        "list_categories",
    )
    list_filter = ("publication_date", "author", "categories")
    search_fields = ("title", "content", "author__email", "author__username")
    raw_id_fields = ("author",)
    date_hierarchy = "publication_date"
    inlines = [CommentInline]
    readonly_fields = ("publication_date", "image_preview_admin")

    filter_horizontal = ("categories",)
    fields = (
        "title",
        "author",
        "categories",
        "content",
        "main_image",
        "image_preview_admin",
        "publication_date",
    )

    @admin.display(description=_("Категории"))
    def list_categories(self, obj):
        return ", ".join([c.name for c in obj.categories.all()])

    @admin.display(description=_("Email автора"), ordering="author__email")
    def author_email(self, obj):
        return obj.author.email if obj.author else _("Нет автора")

    @admin.display(description=_("Дата публикации"), ordering="publication_date")
    def publication_date_formatted(self, obj):
        return obj.publication_date.strftime("%d.%m.%Y %H:%M")

    @admin.display(description=_("Кол-во комментариев"))
    def comment_count(self, obj):
        return obj.comments.count()

    @admin.display(description=_("Превью изображения"))
    def image_preview_admin(self, obj):
        if obj.main_image:
            return format_html(
                '<img src="{}" style="max-height: 200px; max-width: 200px;" />',
                obj.main_image.url,
            )
        return _("Нет изображения")

    @admin.display(description=_("Превью (список)"))
    def image_preview_list(self, obj):
        if obj.main_image:
            return format_html(
                '<img src="{}" style="max-height: 50px; max-width: 50px;" />',
                obj.main_image.url,
            )
        return _("Нет изобр.")


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "article_link", "user_email", "short_text", "date_created")
    list_filter = ("date_created", "article__title")
    search_fields = ("text", "user__email", "user__username", "article__title")
    raw_id_fields = ("article", "user")
    date_hierarchy = "date_created"
    readonly_fields = ("date_created",)

    @admin.display(description=_("Статья"), ordering="article__title")
    def article_link(self, obj):
        from django.urls import reverse

        link = reverse("admin:siteapp_article_change", args=[obj.article.id])
        return format_html('<a href="{}">{}</a>', link, str(obj.article))

    @admin.display(description=_("Email пользователя"), ordering="user__email")
    def user_email(self, obj):
        return obj.user.email

    @admin.display(description=_("Текст (кратко)"), ordering="text")
    def short_text(self, obj):
        return (obj.text[:75] + "...") if len(obj.text) > 75 else obj.text


@admin.register(Volunteering)
class VolunteeringAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user_email",
        "shelter_name",
        "start_date_formatted",
        "end_date_formatted",
    )
    list_filter = ("start_date", "shelter", "user__region")
    search_fields = ("user__email", "user__username", "shelter__name", "notes")
    raw_id_fields = ("user", "shelter")
    date_hierarchy = "start_date"

    @admin.display(description=_("Email волонтёра"), ordering="user__email")
    def user_email(self, obj):
        return obj.user.email

    @admin.display(description=_("Приют"), ordering="shelter__name")
    def shelter_name(self, obj):
        return obj.shelter.name

    @admin.display(description=_("Дата начала"), ordering="start_date")
    def start_date_formatted(self, obj):
        return obj.start_date.strftime("%d.%m.%Y %H:%M")

    @admin.display(description=_("Дата окончания"), ordering="end_date")
    def end_date_formatted(self, obj):
        return obj.end_date.strftime("%d.%m.%Y %H:%M") if obj.end_date else _("Активно")
