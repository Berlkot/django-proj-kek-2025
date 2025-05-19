# siteapp/serializers.py
from rest_framework import serializers
from .models import (
    Advertisement, AdPhoto, Article, User, Region, Species, AdStatus,
    AnimalColor, AnimalGender, Animal, AdResponse, Role, ArticleCategory,
    Comment
)
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer
from djoser.serializers import UserSerializer as BaseUserSerializer



class CommentAuthorSerializer(serializers.ModelSerializer): # Похож на AdDetailAuthorSerializer
    avatar_url = serializers.CharField(read_only=True) # Из свойства модели User
    class Meta:
        model = User
        fields = ['id', 'display_name', 'avatar_url']

class CommentSerializer(serializers.ModelSerializer):
    user = CommentAuthorSerializer(read_only=True)
    date_created = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S.%fZ", read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'article', 'user', 'text', 'date_created']
        read_only_fields = ['article', 'user', 'date_created'] # article и user устанавливаются в perform_create
# Вспомогательный сериализатор для фото, если нужно будет больше деталей
class AdPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdPhoto
        fields = ['id', 'image_url'] # Используем image_url из модели

class MinimalUserSerializer(serializers.ModelSerializer):
    region = serializers.StringRelatedField()
    class Meta:
        model = User
        fields = ['id', 'display_name', 'region']

class HomePageAdSerializer(serializers.ModelSerializer):
    first_photo_url = serializers.SerializerMethodField()
    # Предполагаем, что "локация" для объявления - это регион пользователя, создавшего объявление.
    # Если у объявления есть свое поле локации, используйте его.
    location = serializers.SerializerMethodField()
    short_description = serializers.SerializerMethodField()
    species_name = serializers.CharField(source='animal.species.name', read_only=True)
    publication_date = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S.%fZ", read_only=True)
    status_name = serializers.CharField(source='status.name', read_only=True)

    class Meta:
        model = Advertisement
        fields = [
            'id',
            'title',
            'short_description',
            'publication_date',
            'first_photo_url',
            'location',
            'species_name', # Добавлено для возможной фильтрации или отображения
            'status_name', 
        ]

    def get_first_photo_url(self, obj):
        first_photo = obj.photos.first()
        if first_photo and first_photo.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(first_photo.image.url)
            return first_photo.image.url
        return None # Или URL плейсхолдера

    def get_location(self, obj):
        if obj.user and obj.user.region:
            return obj.user.region.name
        # Если у объявления есть свои поля latitude/longitude,
        # можно было бы попытаться получить город, но это сложнее.
        # Или если у Advertisement есть прямое поле region/city.
        return "Не указано"

    def get_short_description(self, obj):
        # Укорачиваем описание для карточки
        if obj.description:
            return (obj.description[:120] + '...') if len(obj.description) > 120 else obj.description
        return ""


class HomePageArticleSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.display_name', allow_null=True, read_only=True)
    excerpt = serializers.SerializerMethodField()
    main_image_url = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = [
            'id',
            'title',
            'excerpt',
            'publication_date',
            'author_name',
            'main_image_url',
        ]

    def get_excerpt(self, obj):
        if obj.content:
            return (obj.content[:150] + '...') if len(obj.content) > 150 else obj.content
        return ""

    def get_main_image_url(self, obj):
        if obj.main_image and obj.main_image.url:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.main_image.url)
            return obj.main_image.url
        return None

class ArticleCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ArticleCategory
        fields = ['id', 'name', 'slug']

class ArticleListSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.display_name', allow_null=True, read_only=True)
    main_image_url = serializers.SerializerMethodField()
    excerpt = serializers.CharField(read_only=True) 
    categories = ArticleCategorySerializer(many=True, read_only=True)
    # Явное указание формата для консистентности с JS new Date()
    publication_date = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S.%fZ", read_only=True)


    class Meta:
        model = Article
        fields = [
            'id',
            'title',
            'excerpt',
            'publication_date',
            'author_name',
            'main_image_url',
            'categories',
        ]

    def get_main_image_url(self, obj):
        if obj.main_image and obj.main_image.url:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.main_image.url)
            return obj.main_image.url
        return None
        

class ArticleAuthorSerializer(serializers.ModelSerializer):
    avatar_url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'display_name', 'avatar_url']

    def get_avatar_url(self, obj):
        if obj.avatar and hasattr(obj.avatar, 'url'):
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.avatar.url)
            return obj.avatar.url
        # Возвращаем URL для плейсхолдера, если нет аватара
        # Убедитесь, что этот плейсхолдер доступен в static/images/
        # или предоставьте полный URL к внешнему плейсхолдеру
        # request = self.context.get('request')
        # if request:
        #     return request.build_absolute_uri('/static/images/avatar-placeholder.png')
        return None # Или статический URL плейсхолдера

class ArticleDetailSerializer(serializers.ModelSerializer):
    author = ArticleAuthorSerializer(read_only=True)
    main_image_url = serializers.SerializerMethodField()
    categories = ArticleCategorySerializer(many=True, read_only=True) # Если не было
    comments = CommentSerializer(many=True, read_only=True) # <-- ДОБАВЛЕНО

    class Meta:
        model = Article
        fields = [
            'id', 'title', 'content', 'publication_date', 'author',
            'main_image_url', 'categories', 'comments', # <-- ДОБАВЛЕНО comments
        ]

    def get_main_image_url(self, obj):
        if obj.main_image and hasattr(obj.main_image, 'url'):
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.main_image.url)
            return obj.main_image.url
        return None # Или URL плейсхолдера


class AdListAdPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdPhoto
        fields = ['id', 'image_url']

class AdListAnimalSerializer(serializers.ModelSerializer):
    species = serializers.StringRelatedField()
    breed = serializers.StringRelatedField()
    color = serializers.StringRelatedField()
    gender = serializers.StringRelatedField()

    class Meta:
        model = Animal
        fields = ['name', 'species', 'breed', 'color', 'gender', 'birth_date']

class AdListUserSerializer(serializers.ModelSerializer):
    region = serializers.StringRelatedField()
    class Meta:
        model = User
        fields = ['id', 'display_name', 'region']


class AdvertisementListSerializer(serializers.ModelSerializer):
    animal = AdListAnimalSerializer(read_only=True)
    user = AdListUserSerializer(read_only=True) # Используем упрощенный сериализатор для пользователя
    status = serializers.StringRelatedField() # Название статуса (типа объявления)
    first_photo_url = serializers.SerializerMethodField()
    location = serializers.SerializerMethodField() # Будет регионом пользователя
    # publication_date оставляем как есть, форматирование на фронте
    publication_date = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S.%fZ", read_only=True)
    short_description = serializers.SerializerMethodField()

    class Meta:
        model = Advertisement
        fields = [
            'id',
            'title',
            'animal',
            'user',
            'status',
            'short_description',
            'publication_date',
            'latitude',
            'longitude',
            'first_photo_url',
            'location',
        ]

    def get_first_photo_url(self, obj):
        first_photo = obj.photos.first()
        if first_photo and first_photo.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(first_photo.image.url)
            return first_photo.image.url
        return None

    def get_location(self, obj):
        # Пока что локация объявления - это регион пользователя
        if obj.user and obj.user.region:
            return obj.user.region.name
        # Если у Advertisement будет свое поле region, то использовать его
        # if obj.region:
        #     return obj.region.name
        return "Не указано"

    def get_short_description(self, obj):
        if obj.description:
            return (obj.description[:100] + '...') if len(obj.description) > 100 else obj.description
        return ""

# Сериализаторы для опций фильтров
class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = ['id', 'name']

class SpeciesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Species
        fields = ['id', 'name']

class AdStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdStatus
        fields = ['id', 'name']

class AnimalColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnimalColor
        fields = ['id', 'name']

class AnimalGenderSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnimalGender
        fields = ['id', 'name']
        
        
class AdDetailAuthorSerializer(serializers.ModelSerializer):
    avatar_url = serializers.SerializerMethodField()
    role = serializers.StringRelatedField() # Имя роли

    class Meta:
        model = User
        fields = ['id', 'display_name', 'role', 'phone_number', 'email', 'avatar_url', 'region'] # Добавлены role, phone_number, email, region (id региона)
        # 'region' здесь вернет ID, если нужно имя, можно использовать serializers.StringRelatedField(source='region')
        # или кастомный метод, но для API лучше передавать ID, а на фронте иметь список регионов.
        # Но для простоты пока оставим StringRelatedField, если он уже есть у User.
        # Если у User поле region это ForeignKey, тоserializers.StringRelatedField() вернет имя.

    def get_avatar_url(self, obj):
        if obj.avatar and hasattr(obj.avatar, 'url'):
            request = self.context.get('request')
            return request.build_absolute_uri(obj.avatar.url) if request else obj.avatar.url
        return None

# Для информации о животном в деталях объявления
class AdDetailAnimalSerializer(serializers.ModelSerializer):
    species = serializers.StringRelatedField()
    breed = serializers.StringRelatedField()
    color = serializers.StringRelatedField()
    gender = serializers.StringRelatedField()
    age_years_months = serializers.SerializerMethodField() # Вычисляемый возраст

    class Meta:
        model = Animal
        fields = ['id', 'name', 'species', 'breed', 'color', 'gender', 'birth_date', 'age_years_months']

    def get_age_years_months(self, obj):
        if not obj.birth_date:
            return "Неизвестно"
        
        today = timezone.now().date()
        delta = relativedelta(today, obj.birth_date)
        
        years = delta.years
        months = delta.months
        # days = delta.days # Дни пока не используем в строке

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
        
        if not age_parts: # Если очень молодой (меньше месяца)
            # Считаем дни, если животному меньше месяца
            days_total = (today - obj.birth_date).days
            if days_total == 1:
                 return f"{days_total} день"
            elif days_total < 5 :
                 return f"{days_total} дня"
            elif days_total < 21 : # 5-20 дней
                 return f"{days_total} дней"
            elif days_total % 10 == 1:
                 return f"{days_total} день"
            elif days_total % 10 in [2,3,4]:
                 return f"{days_total} дня"
            else: # 25-30 дней
                 return f"{days_total} дней"


        return ", ".join(age_parts) if age_parts else "Меньше месяца"

# Для фотографий объявления в деталях
class AdDetailPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdPhoto
        fields = ['id', 'image_url'] # Используем свойство image_url из модели

# Для комментариев/откликов
class AdResponseSerializer(serializers.ModelSerializer):
    user = AdDetailAuthorSerializer(read_only=True) # Информация об авторе комментария
    date_created = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S.%fZ", read_only=True)

    class Meta:
        model = AdResponse
        fields = ['id', 'user', 'message', 'date_created']


class AdvertisementDetailSerializer(serializers.ModelSerializer):
    animal = AdDetailAnimalSerializer(read_only=True)
    user = AdDetailAuthorSerializer(read_only=True) # Автор объявления
    status = serializers.StringRelatedField()
    photos = AdDetailPhotoSerializer(many=True, read_only=True)
    responses = AdResponseSerializer(many=True, read_only=True) # Комментарии/отклики
    # publication_date форматируется на фронте, передаем как есть
    publication_date = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S.%fZ", read_only=True)
    location = serializers.SerializerMethodField() # Регион пользователя, если есть

    class Meta:
        model = Advertisement
        fields = [
            'id',
            'title',
            'description', # Полное описание
            'animal',
            'user',
            'status',
            'publication_date',
            'latitude',
            'longitude',
            'photos',
            'responses',
            'location',
        ]

    def get_location(self, obj):
        if obj.user and obj.user.region:
            return obj.user.region.name
        return "Не указано"

class UserCreateSerializer(BaseUserCreateSerializer):
    # Можно добавить дополнительные поля для регистрации, если они нужны и не являются частью AbstractUser
    # Например, display_name, region_id, role_id
    # region = serializers.PrimaryKeyRelatedField(queryset=Region.objects.all(), allow_null=True, required=False)
    # role = serializers.PrimaryKeyRelatedField(queryset=Role.objects.all(), allow_null=True, required=False)

    class Meta(BaseUserCreateSerializer.Meta):
        model = User
        fields = ('id', 'email', 'username', 'password', 'display_name', 'first_name', 'last_name', 'region', 'role')
        # Добавили 'display_name', 'first_name', 'last_name', 'region', 'role'
        # 'region' и 'role' должны принимать ID при создании.

    # Если вы хотите автоматически создавать display_name из username, если он не предоставлен:
    # def create(self, validated_data):
    #     if 'display_name' not in validated_data or not validated_data['display_name']:
    #         validated_data['display_name'] = validated_data.get('username')
    #     return super().create(validated_data)


class CurrentUserSerializer(BaseUserSerializer):
    # Сериализатор для эндпоинта /users/me/
    # Djoser по умолчанию использует email, username. Добавим нужные нам поля.
    avatar_url = serializers.CharField(read_only=True) # Используем свойство из модели
    role = serializers.StringRelatedField(read_only=True)
    region = serializers.StringRelatedField(read_only=True)

    class Meta(BaseUserSerializer.Meta):
        model = User
        fields = (
            'id', 'email', 'username', 'display_name', 'first_name', 'last_name',
            'avatar_url', 'role', 'region', 'phone_number', 'is_staff'
            # Добавьте другие поля, которые хотите видеть для /users/me/
        )
        read_only_fields = ('email', 'is_staff', 'role', 'region', 'avatar_url') # email нельзя менять через /me/ по умолчанию
        # Если хотите разрешить редактирование каких-то полей через /users/me/ (PUT/PATCH), уберите их из read_only_fields

class ArticleManageSerializer(serializers.ModelSerializer):
    # author устанавливается автоматически из request.user
    # categories можно передавать как список ID
    categories = serializers.PrimaryKeyRelatedField(
        queryset=ArticleCategory.objects.all(), 
        many=True, 
        required=False # Категории могут быть необязательными
    )
    # main_image будет обрабатываться как FileUpload

    class Meta:
        model = Article
        fields = ['id', 'title', 'content', 'main_image', 'categories', 'author', 'publication_date']
        read_only_fields = ['id', 'author', 'publication_date'] # author и publication_date устанавливаются автоматически

    def create(self, validated_data):
        # Устанавливаем автора при создании
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)

    # Метод update по умолчанию должен работать нормально для main_image и categories.
    # Если main_image передано как null, оно будет очищено (если blank=True, null=True в модели).
    # Если main_image не передано, оно останется без изменений.




    # Если article не передается в URL, а в данных запроса:
    # def create(self, validated_data):
    #     validated_data['user'] = self.context['request'].user
    #     return super().create(validated_data)