# siteapp/serializers.py
from rest_framework import serializers
from .models import (
    Advertisement, AdPhoto, Article, User, Region, Species, AdStatus,
    AnimalColor, AnimalGender, Animal, ArticleCategory
)
from django.utils import timezone
from dateutil.relativedelta import relativedelta

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
    # publication_date форматируется на фронтенде, передаем как есть
    # categories = ArticleCategorySerializer(many=True, read_only=True) # Можно добавить при необходимости

    class Meta:
        model = Article
        fields = [
            'id',
            'title',
            'content', # Полное содержимое статьи (может быть HTML)
            'publication_date',
            'author',
            'main_image_url',
            # 'categories',
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