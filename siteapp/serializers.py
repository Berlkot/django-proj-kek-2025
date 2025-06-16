import datetime
import typing
from rest_framework import serializers
from .models import (
    Advertisement,
    AdPhoto,
    Article,
    User,
    Region,
    Species,
    AdStatus,
    AnimalColor,
    Animal,
    AdResponse,
    Role,
    ArticleCategory,
    Comment,
    Breed,
    AdvertisementRating
)
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer
from djoser.serializers import UserSerializer as BaseUserSerializer
from django.utils.translation import gettext_lazy as _


class CommentAuthorSerializer(serializers.ModelSerializer):
    """
    Сериализатор для автора комментария.

    Поля:
    - id: идентификатор пользователя,
    - display_name: отображаемое имя пользователя,
    - username: имя пользователя,
    - avatar_url: URL-адрес аватара пользователя
    """
    avatar_url = serializers.SerializerMethodField(
        method_name="get_absolute_avatar_url"
    )

    class Meta:
        model = User
        fields = ["id", "display_name", "username", "avatar_url"]

    def get_absolute_avatar_url(self, obj: User) -> typing.Optional[str]:
        """
        Возвращает абсолютный URL-адрес аватара пользователя.

        :param obj: экземпляр User
        :return: абсолютный URL-адрес аватара или None, если аватара нет
        """
        request = self.context.get("request")
        relative_avatar_url = obj.avatar_url

        if relative_avatar_url and request:
            return request.build_absolute_uri(relative_avatar_url)
        elif relative_avatar_url:
            return relative_avatar_url
        return None


class CommentSerializer(serializers.ModelSerializer):
    """
    Сериализатор для комментария.

    Поля:
    - id: идентификатор комментария,
    - article: статья, к которой относится комментарий,
    - user: пользователь, оставивший комментарий,
    - text: текст комментария,
    - date_created: дата создания комментария.
    """
    user: CommentAuthorSerializer = CommentAuthorSerializer(read_only=True)
    date_created: datetime = serializers.DateTimeField(
        format="%Y-%m-%dT%H:%M:%S.%fZ", read_only=True
    )

    class Meta:
        model = Comment
        fields = ["id", "article", "user", "text", "date_created"]
        read_only_fields = ["article", "user", "date_created"]


class AdPhotoSerializer(serializers.ModelSerializer):
    """
    Сериализатор для отображения фотографии объявления.

    Поля:
    - id: идентификатор фотографии,
    - image_url: URL фотографии.
    """

    class Meta:
        model = AdPhoto
        fields: list[str] = ["id", "image_url"]


class MinimalUserSerializer(serializers.ModelSerializer):
    """
    Минимальный сериализатор для отображения информации о пользователе.

    Поля:
    - id: идентификатор пользователя,
    - display_name: отображаемое имя,
    - region: регион пользователя.
    """
    region = serializers.StringRelatedField()

    class Meta:
        model = User
        fields: list[str] = ["id", "display_name", "region"]


class HomePageAdSerializer(serializers.ModelSerializer):
    """
    Сериализатор для главной страницы объявлений.

    Поля:
    - first_photo_url: URL первой фотографии объявления,
    - location: местоположение пользователя,
    - short_description: краткое описание объявления,
    - species_name: название вида животного,
    - publication_date: дата публикации объявления,
    - status_name: название статуса объявления.
    """
    first_photo_url: str | None = serializers.SerializerMethodField()
    location: str = serializers.SerializerMethodField()
    short_description: str = serializers.SerializerMethodField()
    species_name: str = serializers.CharField(source="animal.species.name", read_only=True)
    publication_date: serializers.DateTimeField = serializers.DateTimeField(
        format="%Y-%m-%dT%H:%M:%S.%fZ", read_only=True
    )
    status_name: str = serializers.CharField(source="status.name", read_only=True)

    class Meta:
        model = Advertisement
        fields = [
            "id",
            "title",
            "short_description",
            "publication_date",
            "first_photo_url",
            "location",
            "species_name",
            "status_name",
        ]

    def get_first_photo_url(self, obj: Advertisement) -> str | None:
        """
        Возвращает URL первой фотографии объявления или None, если фотографий нет.
        """
        first_photo = obj.photos.first()
        if first_photo and first_photo.image:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(first_photo.image.url)
            return first_photo.image.url
        return None

    def get_location(self, obj: Advertisement) -> str:
        """
        Возвращает название региона пользователя или 'Не указано', если регион не задан.
        """
        if obj.user and obj.user.region:
            return obj.user.region.name
        return "Не указано"

    def get_short_description(self, obj: Advertisement) -> str:
        """
        Возвращает краткое описание объявления, обрезанное до 120 символов, если оно длиннее.
        """
        if obj.description:
            return (
                (obj.description[:120] + "...")
                if len(obj.description) > 120
                else obj.description
            )
        return ""


class HomePageArticleSerializer(serializers.ModelSerializer):
    """
    Сериализатор для статьи на главной странице.

    Поля:
    - id: идентификатор статьи,
    - title: заголовок статьи,
    - excerpt: краткое описание статьи (150 символов),
    - publication_date: дата публикации статьи,
    - author_name: отображаемое имя автора,
    - main_image_url: URL главного изображения.
    """
    author_name: str = serializers.CharField(
        source="author.display_name", allow_null=True, read_only=True
    )
    excerpt: str = serializers.SerializerMethodField()
    main_image_url: str = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = [
            "id",
            "title",
            "excerpt",
            "publication_date",
            "author_name",
            "main_image_url",
        ]

    def get_excerpt(self, obj: Article) -> str:
        if obj.content:
            return (
                (obj.content[:150] + "...")
                if len(obj.content) > 150
                else obj.content
            )
        return ""

    def get_main_image_url(self, obj: Article) -> str:
        if obj.main_image and obj.main_image.url:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(obj.main_image.url)
            return obj.main_image.url
        return None


class ArticleCategorySerializer(serializers.ModelSerializer):
    """
    Сериализатор для категории статей.

    Поля:
    - id: идентификатор категории,
    - name: название категории,
    - slug: слаг категории.
    """

    class Meta:
        model = ArticleCategory
        fields: typing.List[str] = ["id", "name", "slug"]


class ArticleListSerializer(serializers.ModelSerializer):
    """
    Сериализатор для списка статей.

    Поля:
    - id: идентификатор статьи,
    - title: заголовок статьи,
    - excerpt: краткое описание статьи,
    - publication_date: дата публикации статьи,
    - author_name: отображаемое имя автора,
    - main_image_url: URL главного изображения,
    - categories: список категорий, к которым относится статья,
    - comments_count: количество комментариев к статье.
    """
    author_name = serializers.CharField(
        source="author.display_name", allow_null=True, read_only=True
    )
    main_image_url: typing.Optional[str] = serializers.SerializerMethodField()
    excerpt = serializers.CharField(read_only=True)
    categories = ArticleCategorySerializer(many=True, read_only=True)

    publication_date = serializers.DateTimeField(
        format="%Y-%m-%dT%H:%M:%S.%fZ", read_only=True
    )
    comments_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Article
        fields = [
            "id",
            "title",
            "excerpt",
            "publication_date",
            "author_name",
            "main_image_url",
            "categories",
            "comments_count",
        ]

    def get_main_image_url(self, obj: Article) -> typing.Optional[str]:
        """
        Возвращает URL-адрес главного изображения, если оно есть.
        """
        if obj.main_image and hasattr(obj.main_image, "url"):
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(obj.main_image.url)
            return obj.main_image.url

        return None


class ArticleAuthorSerializer(serializers.ModelSerializer):
    """
    Сериализатор для автора статьи.

    Поля:
    - id: идентификатор автора,
    - display_name: отображаемое имя автора,
    - avatar_url: URL аватарки автора.

    """
    avatar_url: typing.Optional[str] = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "display_name", "avatar_url"]

    def get_avatar_url(self, obj: User) -> typing.Optional[str]:
        """
        Возвращает URL-адрес аватара, если он есть.
        """
        if obj.avatar and hasattr(obj.avatar, "url"):
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(obj.avatar.url)
            return obj.avatar.url

        return None


class ArticleDetailSerializer(serializers.ModelSerializer):
    """
    Сериализатор для детальной информации о статье.

    Поля:
    - id: идентификатор статьи,
    - title: заголовок статьи,
    - content: текст статьи,
    - publication_date: дата публикации статьи,
    - author: автор статьи (детали: User),
    - main_image_url: URL главного изображения статьи,
    - categories: список категорий статьи (детали: ArticleCategory),
    - comments: список комментариев к статье (детали: Comment).
    """
    author: ArticleAuthorSerializer = ArticleAuthorSerializer(read_only=True)
    main_image_url: str = serializers.SerializerMethodField()
    categories: typing.List[ArticleCategory] = ArticleCategorySerializer(many=True, read_only=True)
    comments: typing.List[Comment] = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Article
        fields = [
            "id",
            "title",
            "content",
            "publication_date",
            "author",
            "main_image_url",
            "categories",
            "comments",
        ]

    def get_main_image_url(self, obj: Article) -> str:
        if obj.main_image and hasattr(obj.main_image, "url"):
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(obj.main_image.url)
            return obj.main_image.url
        return ""


class AdListAdPhotoSerializer(serializers.ModelSerializer):
    """
    Сериализатор для отображения фотографии объявления в списке объявлений.

    Поля:
    - id: идентификатор фотографии,
    - image_url: URL фотографии.
    """

    class Meta:
        model: type = AdPhoto
        fields: list[str] = ["id", "image_url"]


class AdListAnimalSerializer(serializers.ModelSerializer):
    """
    Сериализатор для отображения информации о животном в списке объявлений.

    Поля:
    - name: кличка животного,
    - species: вид животного,
    - breed: порода животного,
    - color: окрас животного,
    - gender: пол животного,
    - birth_date: дата рождения животного.
    """
    species: serializers.StringRelatedField = serializers.StringRelatedField()
    breed: serializers.StringRelatedField = serializers.StringRelatedField()
    color: serializers.StringRelatedField = serializers.StringRelatedField()
    gender: str = serializers.CharField(
        source="get_gender_display", read_only=True, allow_null=True
    )

    class Meta:
        model: type = Animal
        fields: list[str] = ["name", "species", "breed", "color", "gender", "birth_date"]


class AdListUserSerializer(serializers.ModelSerializer):
    """
    Сериализатор для отображения информации о пользователе в списке объявлений.

    Поля:
    - id: идентификатор пользователя,
    - display_name: отображаемое имя,
    - region: регион пользователя.
    """
    region: serializers.StringRelatedField = serializers.StringRelatedField()

    class Meta:
        model: type = User
        fields: list[str] = ["id", "display_name", "region"]


class AdvertisementListSerializer(serializers.ModelSerializer):
    """
    Сериализатор для отображения списка объявлений.

    Поля:
    - animal: информация о животном,
    - user: информация о пользователе,
    - status: статус объявления,
    - first_photo_url: URL первой фотографии,
    - location: местоположение,
    - publication_date: дата публикации,
    - short_description: краткое описание,
    - comments_count: количество комментариев,
    - average_rating: средний рейтинг,
    - rating_count: количество оценок.
    """
    animal: AdListAnimalSerializer = AdListAnimalSerializer(read_only=True)
    user: AdListUserSerializer = AdListUserSerializer(read_only=True)
    status: serializers.StringRelatedField = serializers.StringRelatedField()
    first_photo_url: serializers.SerializerMethodField = serializers.SerializerMethodField()
    location: serializers.SerializerMethodField = serializers.SerializerMethodField()

    publication_date: serializers.DateTimeField = serializers.DateTimeField(
        format="%Y-%m-%dT%H:%M:%S.%fZ", read_only=True
    )
    short_description: serializers.SerializerMethodField = serializers.SerializerMethodField()
    comments_count: serializers.IntegerField = serializers.IntegerField(read_only=True, required=False)
    average_rating: serializers.FloatField = serializers.FloatField(read_only=True, required=False)
    rating_count: serializers.IntegerField = serializers.IntegerField(read_only=True, required=False)

    class Meta:
        model: type = Advertisement
        fields: list[str] = [
            "id",
            "title",
            "animal",
            "user",
            "status",
            "short_description",
            "publication_date",
            "latitude",
            "longitude",
            "first_photo_url",
            "location",
            "comments_count",
            "average_rating",
            "rating_count"
        ]

    def get_first_photo_url(self, obj: Advertisement) -> str | None:
        first_photo = obj.photos.first()
        if first_photo and first_photo.image:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(first_photo.image.url)
            return first_photo.image.url
        return None

    def get_location(self, obj: Advertisement) -> str:
        if obj.user and obj.user.region:
            return obj.user.region.name
        return "Не указано"

    def get_short_description(self, obj: Advertisement) -> str:
        if obj.description:
            return (
                (obj.description[:100] + "...")
                if len(obj.description) > 100
                else obj.description
            )
        return ""


class RegionSerializer(serializers.ModelSerializer):
    """
    Сериализатор для региона.

    Fields:
    - id - идентификатор,
    - name - название региона,
    """
    class Meta:
        model: Region = Region
        fields: tuple[str, ...] = ["id", "name"]


class SpeciesSerializer(serializers.ModelSerializer):
    """
    Сериализатор для вида животного.

    Fields:
    - id - идентификатор,
    - name - название вида,
    """
    class Meta:
        model: Species = Species
        fields: tuple[str, ...] = ["id", "name"]


class AdStatusSerializer(serializers.ModelSerializer):
    """
    Сериализатор для статуса объявления.

    fields:
    - id - идентификатор,
    - name - название статуса,
    """
    class Meta:
        model = AdStatus
        fields: typing.List[str] = ["id", "name"]


class AnimalColorSerializer(serializers.ModelSerializer):
    """
    Сериализатор для цвета животного.

    fields:
    - id - идентификатор,
    - name - название цвета,
    """

    class Meta:
        model = AnimalColor
        fields: list = ["id", "name"]


class AdDetailAuthorSerializer(serializers.ModelSerializer):
    """
    Сериализатор для автора объявления.

    fields:
    - id - идентификатор,
    - display_name - отображаемое имя,
    - role - роль,
    - phone_number - телефон,
    - email - email,
    - avatar_url - URL-адрес аватара,
    - region - регион.
    """
    avatar_url: typing.Optional[str] = serializers.SerializerMethodField()
    role: str = serializers.StringRelatedField()

    class Meta:
        model = User
        fields = [
            "id",
            "display_name",
            "role",
            "phone_number",
            "email",
            "avatar_url",
            "region",
        ]

    def get_avatar_url(self, obj: User) -> typing.Optional[str]:
        """
        Возвращает URL-адрес аватара.

        :param obj: экземпляр User
        :return: URL-адрес аватара
        """
        if obj.avatar and hasattr(obj.avatar, "url"):
            request = self.context.get("request")
            return (
                request.build_absolute_uri(obj.avatar.url)
                if request
                else obj.avatar.url
            )
        return None


class AdDetailAnimalSerializer(serializers.ModelSerializer):
    """
    Сериализатор для животного в деталях объявления.
    """

    species = serializers.StringRelatedField()
    breed = serializers.StringRelatedField()
    color = serializers.StringRelatedField()
    gender = serializers.CharField(
        source="get_gender_display", read_only=True, allow_null=True
    )
    age_years_months = serializers.SerializerMethodField()

    class Meta:
        model = Animal
        fields = [
            "id",
            "name",
            "species",
            "breed",
            "color",
            "gender",
            "birth_date",
            "age_years_months",
        ]

    def get_age_years_months(self, obj: Animal) -> str:
        """
        Возвращает строку с возрастом животного.

        Если дата рождения не указана, то возвращает "Неизвестно".
        """
        if not obj.birth_date:
            return "Неизвестно"

        today = timezone.now().date()
        delta = relativedelta(today, obj.birth_date)

        years = delta.years
        months = delta.months

        age_parts = []
        if years > 0:
            if years == 1:
                age_parts.append(f"{years} год")
            elif 1 < years < 5:
                age_parts.append(f"{years} года")
            else:
                age_parts.append(f"{years} лет")

        if months > 0:
            if months == 1:
                age_parts.append(f"{months} месяц")
            elif 1 < months < 5:
                age_parts.append(f"{months} месяца")
            else:
                age_parts.append(f"{months} месяцев")

        if not age_parts:

            days_total = (today - obj.birth_date).days
            if days_total == 1:
                return f"{days_total} день"
            elif days_total < 5:
                return f"{days_total} дня"
            elif days_total < 21:
                return f"{days_total} дней"
            elif days_total % 10 == 1:
                return f"{days_total} день"
            elif days_total % 10 in [2, 3, 4]:
                return f"{days_total} дня"
            else:
                return f"{days_total} дней"

        return ", ".join(age_parts) if age_parts else "Меньше месяца"


class AdDetailPhotoSerializer(serializers.ModelSerializer):
    """
    Сериализатор для фото объявления.
    """

    image_url = serializers.SerializerMethodField(method_name="get_absolute_image_url")

    class Meta:
        model = AdPhoto
        fields = ["id", "image", "image_url"]

    def get_absolute_image_url(self, obj: AdPhoto) -> typing.Optional[str]:
        """
        Возвращает абсолютный URL фотографии.

        :param obj: объект фото
        :type obj: AdPhoto
        :return: абсолютный URL фотографии
        :rtype: Optional[str]
        """
        request = self.context.get("request")
        if obj.image and hasattr(obj.image, "url") and request:
            return request.build_absolute_uri(obj.image.url)
        elif obj.image and hasattr(obj.image, "url"):
            return obj.image.url
        return None


# Для комментариев/откликов
class AdResponseSerializer(serializers.ModelSerializer):
    """
    Сериализатор для откликов на объявления.

    :param user: автор отклика
    :type user: dict
    :param message: текст отклика
    :type message: str
    :param date_created: дата создания отклика
    :type date_created: datetime
    """
    user = AdDetailAuthorSerializer(read_only=True)
    date_created = serializers.DateTimeField(
        format="%Y-%m-%dT%H:%M:%S.%fZ", read_only=True
    )

    class Meta:
        model = AdResponse
        fields = ["id", "user", "message", "date_created"]


class AdvertisementDetailSerializer(serializers.ModelSerializer):
    """
    Сериализатор для детального просмотра объявления.
    """
    animal = AdDetailAnimalSerializer(read_only=True)
    user = AdDetailAuthorSerializer(read_only=True)
    status = serializers.StringRelatedField()
    photos = AdDetailPhotoSerializer(many=True, read_only=True)
    responses = AdResponseSerializer(many=True, read_only=True)

    publication_date = serializers.DateTimeField(
        format="%Y-%m-%dT%H:%M:%S.%fZ", read_only=True
    )
    location = serializers.SerializerMethodField()
    
    comments_count = serializers.IntegerField(read_only=True, required=False)
    average_rating = serializers.FloatField(read_only=True, required=False)
    rating_count = serializers.IntegerField(read_only=True, required=False)

    class Meta:
        model = Advertisement
        fields = [
            "id",
            "title",
            "description",
            "animal",
            "user",
            "status",
            "publication_date",
            "latitude",
            "longitude",
            "photos",
            "responses",
            "location",
            "comments_count",
            "average_rating",
            "rating_count",
        ]

    def get_location(self, obj: Advertisement) -> str:
        """
        Возвращает регион, указанный в профилях авторизованных пользователей.
        """
        if obj.user and obj.user.region:
            return obj.user.region.name
        return "Не указано"


class UserCreateSerializer(BaseUserCreateSerializer):
    """
    Сериализатор для создания пользователя.
    """

    class Meta(BaseUserCreateSerializer.Meta):
        model = User

        fields = (
            "id",
            "email",
            "username",
            "password",
            "display_name",
            "first_name",
            "last_name",
            'phone_number'
        )

    def create(self, validated_data: typing.Dict[str, typing.Any]) -> User:
        """
        Создает пользователя.

        Если поле `display_name` не заполнено, то оно будет заполнено значением
        из поля `username`.

        :param validated_data: Валидированные данные пользователя
        :return: Новый пользователь
        """
        if "display_name" not in validated_data or not validated_data.get(
            "display_name"
        ):
            if validated_data.get("username"):
                validated_data["display_name"] = validated_data.get("username")
        if 'phone_number' in validated_data and not validated_data['phone_number']:
            validated_data['phone_number'] = None

        user = super().create(validated_data)

        try:
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
            user.role = default_role
            user.save(update_fields=["role"])
        except Exception as e:
            print(
                f"ERROR: Could not assign default role to user {user.email}. Error: {e}"
            )

        return user


class RolePermissionsSerializer(serializers.ModelSerializer):
    """
    Сериализатор прав роли.

    """

    can_create_article: bool = serializers.BooleanField(
        label="Может создавать статьи", read_only=True
    )
    can_edit_own_article: bool = serializers.BooleanField(
        label="Может редактировать свои статьи", read_only=True
    )
    can_edit_any_article: bool = serializers.BooleanField(
        label="Может редактировать любые статьи", read_only=True
    )
    can_delete_own_article: bool = serializers.BooleanField(
        label="Может удалять свои статьи", read_only=True
    )
    can_delete_any_article: bool = serializers.BooleanField(
        label="Может удалять любые статьи", read_only=True
    )
    can_edit_own_comment: bool = serializers.BooleanField(
        label="Может редактировать свои комментарии", read_only=True
    )
    can_delete_own_comment: bool = serializers.BooleanField(
        label="Может удалять свои комментарии", read_only=True
    )
    can_delete_any_comment: bool = serializers.BooleanField(
        label="Может удалять любые комментарии", read_only=True
    )
    can_create_advertisement: bool = serializers.BooleanField(
        label="Может создавать объявления", read_only=True
    )
    can_edit_own_advertisement: bool = serializers.BooleanField(
        label="Может редактировать свои объявления", read_only=True
    )
    can_delete_own_advertisement: bool = serializers.BooleanField(
        label="Может удалять свои объявления", read_only=True
    )
    can_manage_any_advertisement: bool = serializers.BooleanField(
        label="Может управлять любыми объявлениями", read_only=True
    )

    class Meta:
        model = Role
        fields = [
            "can_create_article",
            "can_edit_own_article",
            "can_edit_any_article",
            "can_delete_own_article",
            "can_delete_any_article",
            "can_edit_own_comment",
            "can_delete_own_comment",
            "can_delete_any_comment",
            "can_create_advertisement",
            "can_edit_own_advertisement",
            "can_delete_own_advertisement",
            "can_manage_any_advertisement",
        ]


class CurrentUserSerializer(BaseUserSerializer):
    """
    Сериализатор для текущего пользователя.

    """
    avatar_url = serializers.SerializerMethodField(method_name='get_absolute_avatar_url')
    role_name = serializers.CharField(
        source="role.name", read_only=True, allow_null=True
    )
    region_name = serializers.CharField(
        source="region.name", read_only=True, allow_null=True
    )
    role_permissions = RolePermissionsSerializer(
        source="role", read_only=True, allow_null=True
    )

    class Meta(BaseUserSerializer.Meta):
        model = User
        fields = (
            "id",
            "email",
            "username",
            "display_name",
            "first_name",
            "last_name",
            "avatar_url",
            "role_name",
            "region_name",
            "phone_number",
            "is_staff",
            "role_permissions",
        )
        read_only_fields = (
            "email",
            "is_staff",
            "role_name",
            "region_name",
            "avatar_url",
            "role_permissions",
        )

    def get_absolute_avatar_url(self, obj: User) -> typing.Optional[str]:
        """
        Возвращает URL-адрес аватара.

        :param obj: экземпляр User
        :return: URL-адрес аватара
        """
        request = self.context.get('request')
        relative_avatar_url = obj.avatar_url

        if relative_avatar_url and request:
            return request.build_absolute_uri(relative_avatar_url)
        elif relative_avatar_url:
            return relative_avatar_url
        return None


class ArticleManageSerializer(serializers.ModelSerializer):
    """
    Сериализатор для управления статьями.

    categories - категории статьи,
    title - заголовок статьи,
    content - содержимое статьи,
    main_image - главное изображение статьи,
    author - автор статьи (автоматически подставляется текущий пользователь),
    publication_date - дата публикации статьи (автоматически подставляется текущая дата и время).
    """

    categories = serializers.PrimaryKeyRelatedField(
        queryset=ArticleCategory.objects.all(), many=True, required=False
    )

    class Meta:
        model = Article
        fields = [
            "id",
            "title",
            "content",
            "main_image",
            "categories",
            "author",
            "publication_date",
        ]
        read_only_fields = ["id", "author", "publication_date"]

    def create(self, validated_data: typing.Dict[str, typing.Any]) -> Article:
        """
        Создает статью.

        :param validated_data: Проверенные данные.
        :return: Созданная статья.
        """
        validated_data["author"] = self.context["request"].user
        return super().create(validated_data)


class AnimalNestedManageSerializer(serializers.ModelSerializer):
    """
    Сериализатор для управления животными в составе объявления.

    name - кличка животного,
    birth_date - дата рождения животного,
    species - вид животного,
    breed - порода животного,
    color - окрас животного,
    gender - пол животного.
    """

    species = serializers.PrimaryKeyRelatedField(
        queryset=Species.objects.all(), allow_null=False, label=_("Вид животного")
    )
    breed = serializers.PrimaryKeyRelatedField(
        queryset=Breed.objects.all(), allow_null=True, required=False, label=_("Порода животного")
    )
    color = serializers.PrimaryKeyRelatedField(
        queryset=AnimalColor.objects.all(), allow_null=True, required=False, label=_("Окрас животного")
    )
    gender = serializers.ChoiceField(
        choices=Animal.GENDER_CHOICES, allow_null=True, required=False, label=_("Пол животного")
    )

    class Meta:
        model = Animal
        fields = ["name", "birth_date", "species", "breed", "color", "gender"]

    def validate(self, data: dict[str, typing.Any]) -> dict[str, typing.Any]:
        """
        Проверяет, что выбранная порода соответствует выбранному виду.
        """
        species = data.get('species')
        breed = data.get('breed')

        if species and breed:
            if breed.species != species:
                raise serializers.ValidationError({
                    'breed': _("Выбранная порода '{breed_name}' не соответствует выбранному виду '{species_name}'.")
                             .format(breed_name=breed.name, species_name=species.name)
                })
        return data


class AdPhotoManageSerializer(serializers.ModelSerializer):
    """
    Сериализатор для управления фотографиями объявлений.

    id - идентификатор фотографии,
    image - файл изображения.
    """

    class Meta:
        model = AdPhoto
        fields: tuple[str, ...] = ["id", "image"]

class AdvertisementManageSerializer(serializers.ModelSerializer):
    """
    Сериализатор для управления объявлениями.

    id - идентификатор объявления,
    title - заголовок объявления,
    description - описание объявления,
    status - статус объявления,
    latitude - широта,
    longitude - долгота,
    animal_data - данные об животном (имя, дата рождения, вид, порода, цвет, пол).
    """
    animal_data = AnimalNestedManageSerializer(write_only=True)
    status = serializers.PrimaryKeyRelatedField(queryset=AdStatus.objects.all())

    class Meta:
        model = Advertisement
        fields = [
            "id",
            "title",
            "description",
            "status",
            "latitude",
            "longitude",
            "animal_data",
        ]
        read_only_fields = ["id"]

    def validate_status(self, value: AdStatus) -> AdStatus:
        """
        Валидация статуса объявления.

        Проверяет, может ли пользователь изменить статус объявления.
        """
        user = self.context["request"].user

        if self.instance and self.instance.user == user and not (user.is_staff or (user.role and user.role.can_manage_any_advertisement)):
            allowed_transitions = {
                "Потеряно": ["Найдено", "В архиве"],
                "Найдено": ["Передано владельцу", "В архиве"],

            }
            if self.instance.status.name in allowed_transitions and value.name not in allowed_transitions[self.instance.status.name]:
                raise serializers.ValidationError(f"Вы не можете изменить статус с '{self.instance.status.name}' на '{value.name}'.")
            elif self.instance.status.name not in allowed_transitions and value.id != self.instance.status_id:
                 raise serializers.ValidationError("Вы не можете изменить текущий статус объявления.")

        return value
    
    def validate(self, data):
        """
        Общая валидация данных.
        """
        user = self.context['request'].user
        description = data.get('description')
        latitude = data.get('latitude')
        longitude = data.get('longitude')

        if not self.instance and description:
            active_like_statuses = AdStatus.objects.filter(name__in=["Найдено", "Потеряно", "Требует модерации"])
            
            queryset = Advertisement.objects.filter(
                user=user,
                description__iexact=description,
                status__in=active_like_statuses
            )

            if latitude is not None and longitude is not None:
                queryset = queryset.filter(latitude=latitude, longitude=longitude)

            if queryset.exists():
                raise serializers.ValidationError(
                    _("У вас уже есть активное объявление с похожим описанием. Пожалуйста, проверьте ваши существующие объявления.")
                )
        return data


    def create(self, validated_data: dict) -> Advertisement:
        """
        Создает новое объявление.
        """
        animal_data = validated_data.pop('animal_data')
        animal = Animal.objects.create(**animal_data)
        
        validated_data['animal'] = animal
        validated_data['user'] = self.context['request'].user

        if 'status' not in validated_data or not validated_data.get('status'):
            try:
                default_status_name = "Требует модерации"
                default_status = AdStatus.objects.get(name=default_status_name)
                validated_data['status'] = default_status
            except AdStatus.DoesNotExist:
                raise serializers.ValidationError(
                    {"status": f"Ошибка конфигурации: статус по умолчанию '{default_status_name}' не найден."}
                )
        
        advertisement = Advertisement.objects.create(**validated_data)

        uploaded_photos = self.context["request"].FILES.getlist("photos_upload")
        for photo_file in uploaded_photos:
            AdPhoto.objects.create(advertisement=advertisement, image=photo_file)

        return advertisement

    def update(self, instance: Advertisement, validated_data: dict) -> Advertisement:
        """
        Обновляет существующее объявление.
        """
        animal_instance = instance.animal

        animal_data = validated_data.pop("animal_data", None)

        if animal_data: 
            if "name" in animal_data: animal_instance.name = animal_data.pop("name", animal_instance.name)
            if "birth_date" in animal_data: animal_instance.birth_date = animal_data.pop("birth_date", animal_instance.birth_date)
            if "species" in animal_data: animal_instance.species = animal_data.pop("species", animal_instance.species)
            if "breed" in animal_data: animal_instance.breed = animal_data.pop("breed", animal_instance.breed)
            if "color" in animal_data: animal_instance.color = animal_data.pop("color", animal_instance.color)
            if "gender" in animal_data: animal_instance.gender = animal_data.pop("gender", animal_instance.gender)
            animal_instance.save()

        user = self.context['request'].user
        if 'status' in validated_data and not (user.is_staff or (user.role and user.role.can_manage_any_advertisement)):
            current_status_in_request = validated_data.get('status')
            if current_status_in_request and current_status_in_request != instance.status:
                 try:
                    self.validate_status(current_status_in_request)
                 except serializers.ValidationError:
                    validated_data.pop('status')

        instance = super().update(instance, validated_data)

        uploaded_photos = self.context["request"].FILES.getlist("photos_upload")
        delete_photo_ids_str = self.context["request"].POST.getlist("delete_photos")
        if delete_photo_ids_str:
            AdPhoto.objects.filter(
                advertisement=instance, id__in=map(int, delete_photo_ids_str)
            ).delete()
        for photo_file in uploaded_photos:
            AdPhoto.objects.create(advertisement=instance, image=photo_file)

        return instance


class BreedSerializer(serializers.ModelSerializer):
    """
    Сериализатор для породы животных.

    id - идентификатор породы,
    name - название породы,
    species_id - идентификатор вида животного.
    """

    species_id = serializers.IntegerField(source='species.id', help_text="Идентификатор вида животного")

    class Meta:
        model = Breed
        fields = ["id", "name", "species_id"]


class RegionActivitySerializer(serializers.Serializer):
    """
    Сериализатор для активности региона.

    id - идентификатор региона,
    name - название региона,
    ad_count - количество объявлений в регионе.
    """
    id: int = serializers.IntegerField(source='region__id')
    name: str = serializers.CharField(source='region__name')
    ad_count: int = serializers.IntegerField()


class AdvertisementRatingSerializer(serializers.ModelSerializer):
    """
    Сериализатор для оценки объявления.

    id - идентификатор,
    advertisement - объявление,
    user - пользователь, оставивший оценку,
    rating - оценка,
    created_at - дата оценки.
    """
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = AdvertisementRating
        fields = ['id', 'advertisement', 'user', 'rating', 'created_at']
        read_only_fields = ['id', 'created_at', 'user']

    def validate(self, data: dict) -> dict:
        """
        Валидация оценки объявления.

        :raises serializers.ValidationError: если пользователь уже оставил оценку для этого объявления.
        """
        if not self.instance:
            request_user = self.context['request'].user
            advertisement = data.get('advertisement')
            if AdvertisementRating.objects.filter(advertisement=advertisement, user=request_user).exists():
                raise serializers.ValidationError(_("Вы уже оставили оценку для этого объявления."))
        return data

class RoleSerializer(serializers.ModelSerializer):
    """
    Сериализатор для роли.

    id - идентификатор,
    name - название роли.
    """
    class Meta:
        model: Role = Role
        fields: tuple = ('id', 'name')


class ProfileSerializer(serializers.ModelSerializer):
    """
    Сериализатор для профиля.

    id - идентификатор,
    email - email,
    username - логин,
    display_name - отображаемое имя,
    first_name - имя,
    last_name - фамилия,
    avatar_url - URL-адрес аватара,
    role_name - название роли,
    region_name - название региона,
    phone_number - телефон,
    date_joined - дата регистрации,
    is_staff - является ли пользователь персоналом.
    """
    avatar_url = serializers.SerializerMethodField(method_name='get_absolute_avatar_url')
    role_name = serializers.CharField(source='role.name', read_only=True, allow_null=True)
    region_name = serializers.CharField(source='region.name', read_only=True, allow_null=True)
    date_joined = serializers.DateTimeField(format="%d %B %Y", read_only=True)

    class Meta:
        model = User
        fields = (
            'id', 'email', 'username', 'display_name', 'first_name', 'last_name',
            'avatar_url', 'role_name', 'region_name', 'phone_number', 'date_joined',
            'is_staff'
        )

    def get_absolute_avatar_url(self, obj: User) -> typing.Optional[str]:
        """
        Возвращает URL-адрес аватара.

        :param obj: экземпляр User
        :return: URL-адрес аватара
        """
        request = self.context.get('request')
        if obj.avatar and hasattr(obj.avatar, 'url'):
            return request.build_absolute_uri(obj.avatar.url)
        return None

class ProfileUpdateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для обновления профиля.
    """
    region = serializers.PrimaryKeyRelatedField(
        queryset=Region.objects.all(),
        required=False,
        allow_null=True,
        help_text=_("Регион")
    )
    # Добавляем email
    email = serializers.EmailField(required=False, help_text=_("Email"))

    class Meta:
        model = User
        # Добавляем 'email' в fields
        fields = ('email', 'display_name', 'first_name', 'last_name', 'phone_number', 'region', 'avatar')
        extra_kwargs = {
            'avatar': {'required': False, 'allow_null': True}
        }
    
    def validate_phone_number(self, value: str) -> typing.Optional[str]:
        """
        Валидация телефона.
        """
        if value == '':
            return None
        return value


class AdminProfileUpdateSerializer(ProfileUpdateSerializer):
    """
    Сериализатор для обновления профиля администратора.
    """
    role = serializers.PrimaryKeyRelatedField(queryset=Role.objects.all(), required=False, allow_null=True)

    class Meta(ProfileUpdateSerializer.Meta):
        """
        Метаданные для AdminProfileUpdateSerializer с дополнительными полями.
        """
        fields = ProfileUpdateSerializer.Meta.fields + ('role', 'is_staff')
        
class UserAdminSerializer(serializers.ModelSerializer):
    """
    Сериализатор для списка пользователей в админ-панели.
    """
    role_name = serializers.CharField(source='role.name', read_only=True, allow_null=True)
    region_name = serializers.CharField(source='region.name', read_only=True, allow_null=True)
    
    class Meta:
        model = User
        fields: tuple = (
            'id',
            'email',
            'username',
            'display_name',
            'role_name',
            'region_name',
            'is_staff',
            'is_active',  # Важное поле для отображения статуса
            'date_joined',
        )
