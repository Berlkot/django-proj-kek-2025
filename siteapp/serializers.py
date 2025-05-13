# siteapp/serializers.py
from rest_framework import serializers
from .models import Advertisement, AdPhoto, Article, User, Region

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
    main_image_url = serializers.SerializerMethodField() # Раскомментировано/Добавлено

    class Meta:
        model = Article
        fields = [
            'id',
            'title',
            'excerpt',
            'publication_date',
            'author_name',
            'main_image_url', # Раскомментировано/Добавлено
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
        # Можно вернуть URL плейсхолдера по умолчанию, если изображение отсутствует
        return "https://via.placeholder.com/800x400/cccccc/888888?text=No+Image"