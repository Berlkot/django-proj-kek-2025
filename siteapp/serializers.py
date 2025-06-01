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
)
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer
from djoser.serializers import UserSerializer as BaseUserSerializer


class CommentAuthorSerializer(serializers.ModelSerializer):
    avatar_url = serializers.SerializerMethodField(
        method_name="get_absolute_avatar_url"
    )

    class Meta:
        model = User

        fields = ["id", "display_name", "username", "avatar_url"]

    def get_absolute_avatar_url(self, obj: User):
        request = self.context.get("request")
        relative_avatar_url = obj.avatar_url

        if relative_avatar_url and request:
            return request.build_absolute_uri(relative_avatar_url)
        elif relative_avatar_url:
            return relative_avatar_url
        return None


class CommentSerializer(serializers.ModelSerializer):
    user = CommentAuthorSerializer(read_only=True)
    date_created = serializers.DateTimeField(
        format="%Y-%m-%dT%H:%M:%S.%fZ", read_only=True
    )

    class Meta:
        model = Comment
        fields = ["id", "article", "user", "text", "date_created"]
        read_only_fields = ["article", "user", "date_created"]


class AdPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdPhoto
        fields = ["id", "image_url"]


class MinimalUserSerializer(serializers.ModelSerializer):
    region = serializers.StringRelatedField()

    class Meta:
        model = User
        fields = ["id", "display_name", "region"]


class HomePageAdSerializer(serializers.ModelSerializer):
    first_photo_url = serializers.SerializerMethodField()

    location = serializers.SerializerMethodField()
    short_description = serializers.SerializerMethodField()
    species_name = serializers.CharField(source="animal.species.name", read_only=True)
    publication_date = serializers.DateTimeField(
        format="%Y-%m-%dT%H:%M:%S.%fZ", read_only=True
    )
    status_name = serializers.CharField(source="status.name", read_only=True)

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

    def get_first_photo_url(self, obj):
        first_photo = obj.photos.first()
        if first_photo and first_photo.image:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(first_photo.image.url)
            return first_photo.image.url
        return None

    def get_location(self, obj):
        if obj.user and obj.user.region:
            return obj.user.region.name

        return "Не указано"

    def get_short_description(self, obj):

        if obj.description:
            return (
                (obj.description[:120] + "...")
                if len(obj.description) > 120
                else obj.description
            )
        return ""


class HomePageArticleSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(
        source="author.display_name", allow_null=True, read_only=True
    )
    excerpt = serializers.SerializerMethodField()
    main_image_url = serializers.SerializerMethodField()

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

    def get_excerpt(self, obj):
        if obj.content:
            return (
                (obj.content[:150] + "...") if len(obj.content) > 150 else obj.content
            )
        return ""

    def get_main_image_url(self, obj):
        if obj.main_image and obj.main_image.url:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(obj.main_image.url)
            return obj.main_image.url
        return None


class ArticleCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ArticleCategory
        fields = ["id", "name", "slug"]


class ArticleListSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(
        source="author.display_name", allow_null=True, read_only=True
    )
    main_image_url = serializers.SerializerMethodField()
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

    def get_main_image_url(self, obj):
        if obj.main_image and obj.main_image.url:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(obj.main_image.url)
            return obj.main_image.url
        return None


class ArticleAuthorSerializer(serializers.ModelSerializer):
    avatar_url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "display_name", "avatar_url"]

    def get_avatar_url(self, obj):
        if obj.avatar and hasattr(obj.avatar, "url"):
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(obj.avatar.url)
            return obj.avatar.url

        return None


class ArticleDetailSerializer(serializers.ModelSerializer):
    author = ArticleAuthorSerializer(read_only=True)
    main_image_url = serializers.SerializerMethodField()
    categories = ArticleCategorySerializer(many=True, read_only=True)
    comments = CommentSerializer(many=True, read_only=True)

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

    def get_main_image_url(self, obj):
        if obj.main_image and hasattr(obj.main_image, "url"):
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(obj.main_image.url)
            return obj.main_image.url
        return None


class AdListAdPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdPhoto
        fields = ["id", "image_url"]


class AdListAnimalSerializer(serializers.ModelSerializer):
    species = serializers.StringRelatedField()
    breed = serializers.StringRelatedField()
    color = serializers.StringRelatedField()
    gender = serializers.CharField(
        source="get_gender_display", read_only=True, allow_null=True
    )

    class Meta:
        model = Animal
        fields = ["name", "species", "breed", "color", "gender", "birth_date"]


class AdListUserSerializer(serializers.ModelSerializer):
    region = serializers.StringRelatedField()

    class Meta:
        model = User
        fields = ["id", "display_name", "region"]


class AdvertisementListSerializer(serializers.ModelSerializer):
    animal = AdListAnimalSerializer(read_only=True)
    user = AdListUserSerializer(read_only=True)
    status = serializers.StringRelatedField()
    first_photo_url = serializers.SerializerMethodField()
    location = serializers.SerializerMethodField()

    publication_date = serializers.DateTimeField(
        format="%Y-%m-%dT%H:%M:%S.%fZ", read_only=True
    )
    short_description = serializers.SerializerMethodField()

    class Meta:
        model = Advertisement
        fields = [
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
        ]

    def get_first_photo_url(self, obj):
        first_photo = obj.photos.first()
        if first_photo and first_photo.image:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(first_photo.image.url)
            return first_photo.image.url
        return None

    def get_location(self, obj):

        if obj.user and obj.user.region:
            return obj.user.region.name

        return "Не указано"

    def get_short_description(self, obj):
        if obj.description:
            return (
                (obj.description[:100] + "...")
                if len(obj.description) > 100
                else obj.description
            )
        return ""


class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = ["id", "name"]


class SpeciesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Species
        fields = ["id", "name"]


class AdStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdStatus
        fields = ["id", "name"]


class AnimalColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnimalColor
        fields = ["id", "name"]


class AdDetailAuthorSerializer(serializers.ModelSerializer):
    avatar_url = serializers.SerializerMethodField()
    role = serializers.StringRelatedField()

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

    def get_avatar_url(self, obj):
        if obj.avatar and hasattr(obj.avatar, "url"):
            request = self.context.get("request")
            return (
                request.build_absolute_uri(obj.avatar.url)
                if request
                else obj.avatar.url
            )
        return None


class AdDetailAnimalSerializer(serializers.ModelSerializer):
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

    def get_age_years_months(self, obj):
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

    image_url = serializers.SerializerMethodField(method_name="get_absolute_image_url")

    class Meta:
        model = AdPhoto
        fields = ["id", "image", "image_url"]

    def get_absolute_image_url(self, obj: AdPhoto):
        request = self.context.get("request")
        if obj.image and hasattr(obj.image, "url") and request:
            return request.build_absolute_uri(obj.image.url)
        elif obj.image and hasattr(obj.image, "url"):
            return obj.image.url
        return None


# Для комментариев/откликов
class AdResponseSerializer(serializers.ModelSerializer):
    user = AdDetailAuthorSerializer(read_only=True)
    date_created = serializers.DateTimeField(
        format="%Y-%m-%dT%H:%M:%S.%fZ", read_only=True
    )

    class Meta:
        model = AdResponse
        fields = ["id", "user", "message", "date_created"]


class AdvertisementDetailSerializer(serializers.ModelSerializer):
    animal = AdDetailAnimalSerializer(read_only=True)
    user = AdDetailAuthorSerializer(read_only=True)
    status = serializers.StringRelatedField()
    photos = AdDetailPhotoSerializer(many=True, read_only=True)
    responses = AdResponseSerializer(many=True, read_only=True)

    publication_date = serializers.DateTimeField(
        format="%Y-%m-%dT%H:%M:%S.%fZ", read_only=True
    )
    location = serializers.SerializerMethodField()

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
        ]

    def get_location(self, obj):
        if obj.user and obj.user.region:
            return obj.user.region.name
        return "Не указано"


class UserCreateSerializer(BaseUserCreateSerializer):

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
        )

    def create(self, validated_data):

        print("adafaf")

        if "display_name" not in validated_data or not validated_data.get(
            "display_name"
        ):
            if validated_data.get("username"):
                validated_data["display_name"] = validated_data.get("username")

        user = super().create(validated_data)

        try:
            print(f"Attempting to assign default role to user: {user.email}")
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
                print(
                    f"Default role 'Пользователь' was created with default permissions."
                )
            user.role = default_role
            user.save(update_fields=["role"])
            print(
                f"Successfully assigned role '{user.role.name if user.role else 'None'}' to user {user.email}"
            )
        except Exception as e:
            print(
                f"ERROR: Could not assign default role to user {user.email}. Error: {e}"
            )

        return user


class RolePermissionsSerializer(serializers.ModelSerializer):
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
    avatar_url = serializers.CharField(read_only=True)
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


class ArticleManageSerializer(serializers.ModelSerializer):

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

    def create(self, validated_data):

        validated_data["author"] = self.context["request"].user
        return super().create(validated_data)


class AnimalNestedManageSerializer(serializers.ModelSerializer):
    species = serializers.PrimaryKeyRelatedField(queryset=Species.objects.all())
    breed = serializers.PrimaryKeyRelatedField(
        queryset=Breed.objects.all(), allow_null=True, required=False
    )
    color = serializers.PrimaryKeyRelatedField(
        queryset=AnimalColor.objects.all(), allow_null=True, required=False
    )
    gender = serializers.ChoiceField(
        choices=Animal.GENDER_CHOICES, allow_null=True, required=False
    )

    class Meta:
        model = Animal
        fields = ["name", "birth_date", "species", "breed", "color", "gender"]


class AdPhotoManageSerializer(serializers.ModelSerializer):

    class Meta:
        model = AdPhoto
        fields = ["id", "image"]


class AdvertisementManageSerializer(serializers.ModelSerializer):
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

    def validate_status(self, value):
        user = self.context["request"].user

        allowed_statuses_for_user = ["Потеряно", "Найдено", "Отдам в добрые руки"]

        if not self.instance and not (
            user.is_staff or (user.role and user.role.can_manage_any_advertisement)
        ):
            if value.name not in allowed_statuses_for_user:
                raise serializers.ValidationError(
                    f"Вы не можете установить статус '{value.name}'. Разрешенные статусы: {', '.join(allowed_statuses_for_user)}."
                )

        elif (
            self.instance
            and self.instance.user == user
            and not (
                user.is_staff or (user.role and user.role.can_manage_any_advertisement)
            )
        ):

            pass

        return value

    def create(self, validated_data):
        animal_data = validated_data.pop("animal_data")

        animal = Animal.objects.create(**animal_data)

        validated_data["animal"] = animal
        validated_data["user"] = self.context["request"].user
        advertisement = Advertisement.objects.create(**validated_data)

        uploaded_photos = self.context["request"].FILES.getlist("photos_upload")
        for photo_file in uploaded_photos:
            AdPhoto.objects.create(advertisement=advertisement, image=photo_file)

        return advertisement

    def update(self, instance, validated_data):

        animal_instance = instance.animal
        print(validated_data, "animal_name" in validated_data)

        animal_data = validated_data.pop("animal_data", None)

        if "name" in animal_data:
            animal_instance.name = animal_data.pop("name")
        if "birth_date" in animal_data:
            animal_instance.birth_date = animal_data.pop("birth_date")
        if "species" in animal_data:
            animal_instance.species = animal_data.pop("species")
        if "breed" in animal_data:
            animal_instance.breed = animal_data.pop("breed")
        if "color" in animal_data:
            animal_instance.color = animal_data.pop("color")
        if "gender" in animal_data:
            animal_instance.gender = animal_data.pop("gender")

        animal_instance.save()

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

    species_id = serializers.IntegerField(source="species.id")

    class Meta:
        model = Breed
        fields = ["id", "name", "species_id"]


class RegionActivitySerializer(serializers.Serializer):
    id = serializers.IntegerField(source='region__id')
    name = serializers.CharField(source='region__name')
    ad_count = serializers.IntegerField()