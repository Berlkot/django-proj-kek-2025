# siteapp/serializers.py
from rest_framework import serializers
from .models import (
    Advertisement, AdPhoto, Article, User, Region, Species, AdStatus,
    AnimalColor, Animal, AdResponse, Role, ArticleCategory,
    Comment, Breed
)
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer
from djoser.serializers import UserSerializer as BaseUserSerializer


class CommentAuthorSerializer(serializers.ModelSerializer):
    avatar_url = serializers.SerializerMethodField(method_name='get_absolute_avatar_url')

    class Meta:
        model = User
        # display_name может быть пустым, username - нет (по умолчанию в AbstractUser)
        # Если display_name нет, фронтенд может использовать username
        fields = ['id', 'display_name', 'username', 'avatar_url']

    def get_absolute_avatar_url(self, obj: User):
        request = self.context.get('request')
        relative_avatar_url = obj.avatar_url
        
        if relative_avatar_url and request:
            return request.build_absolute_uri(relative_avatar_url)
        elif relative_avatar_url:
            return relative_avatar_url
        return None # Если у пользователя нет аватара (avatar_url вернул None)

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
    comments_count = serializers.IntegerField(read_only=True)


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
            'comments_count'
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
    gender = serializers.CharField(source='get_gender_display', read_only=True, allow_null=True)

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
    gender = serializers.CharField(source='get_gender_display', read_only=True, allow_null=True)
    age_years_months = serializers.SerializerMethodField()

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
    # Заменяем прямое использование image_url на SerializerMethodField
    # чтобы иметь доступ к контексту запроса для build_absolute_uri
    image_url = serializers.SerializerMethodField(method_name='get_absolute_image_url')
    # Оставляем image для возможности POST/PATCH (если этот сериализатор используется для записи)
    # Если он только для чтения, можно убрать 'image' из fields.
    # Но для AdPhoto он обычно только для чтения в контексте AdvertisementDetailSerializer.

    class Meta:
        model = AdPhoto
        fields = ['id', 'image', 'image_url'] # 'image' - это ImageFieldFile, 'image_url_absolute' - наш полный URL
        # Если 'image' (поле файла) не нужно в ответе, можно убрать:
        # fields = ['id', 'image_url_absolute'] 

    def get_absolute_image_url(self, obj: AdPhoto):
        request = self.context.get('request')
        if obj.image and hasattr(obj.image, 'url') and request:
            return request.build_absolute_uri(obj.image.url)
        elif obj.image and hasattr(obj.image, 'url'): # Фоллбэк, если request нет в контексте
            return obj.image.url 
        return None

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
    
    class Meta(BaseUserCreateSerializer.Meta):
        model = User
        # Поля, которые Djoser будет обрабатывать из запроса
        fields = ('id', 'email', 'username', 'password', 'display_name', 'first_name', 'last_name') 
        # Мы убрали 'region' и 'role' отсюда, так как Djoser не будет их напрямую принимать
        # при стандартном POST на /users/, если они не объявлены как writable поля в сериализаторе.
        # Мы установим 'role' вручную в методе create.
        # 'region' можно обрабатывать аналогично, если он должен устанавливаться при регистрации.

    def create(self, validated_data):
        # если эта строчка когда-нибудь сработает, то можно отключить сигналы для логина
        print('adafaf')
        # Если 'display_name' не пришел или пуст, можно установить его равным 'username'
        # Это нужно делать ДО вызова super().create, если display_name - обязательное поле в модели User
        # или если super().create его как-то использует.
        # Если display_name опциональное, можно и после.
        if 'display_name' not in validated_data or not validated_data.get('display_name'):
             if validated_data.get('username'): # Проверка, что username есть
                validated_data['display_name'] = validated_data.get('username')
        
        user = super().create(validated_data) # Сначала Djoser создает пользователя

        # Затем присваиваем роль по умолчанию
        try:
            print(f"Attempting to assign default role to user: {user.email}") # Отладочный print
            default_role, created = Role.objects.get_or_create(
                name="Пользователь", 
                defaults={ # Если роль создается, можно сразу указать дефолтные права
                    'can_create_advertisement': True,
                    'can_edit_own_advertisement': True,
                    'can_delete_own_advertisement': True,
                    'can_edit_own_comment': True,
                    'can_delete_own_comment': True,
                    # ... и другие базовые права для "Пользователя"
                }
            )
            if created:
                print(f"Default role 'Пользователь' was created with default permissions.")
            user.role = default_role
            user.save(update_fields=['role']) # Важно сохранить изменения
            print(f"Successfully assigned role '{user.role.name if user.role else 'None'}' to user {user.email}")
        except Exception as e:
            print(f"ERROR: Could not assign default role to user {user.email}. Error: {e}")
            # В продакшене здесь должно быть логирование, а не просто print
        
        return user

class RolePermissionsSerializer(serializers.ModelSerializer): # Новый вложенный сериализатор
    class Meta:
        model = Role
        fields = [
            # Статьи
            'can_create_article', 'can_edit_own_article', 'can_edit_any_article',
            'can_delete_own_article', 'can_delete_any_article',
            # Комментарии
            'can_edit_own_comment', 'can_delete_own_comment', 'can_delete_any_comment',
            # ... добавьте другие права по мере необходимости
            'can_create_advertisement', 'can_edit_own_advertisement',
            'can_delete_own_advertisement', 'can_manage_any_advertisement',
        ]

class CurrentUserSerializer(BaseUserSerializer):
    avatar_url = serializers.CharField(read_only=True)
    role_name = serializers.CharField(source='role.name', read_only=True, allow_null=True) # Имя роли
    region_name = serializers.CharField(source='region.name', read_only=True, allow_null=True) # Имя региона
    role_permissions = RolePermissionsSerializer(source='role', read_only=True, allow_null=True) # Права роли

    class Meta(BaseUserSerializer.Meta):
        model = User
        fields = (
            'id', 'email', 'username', 'display_name', 'first_name', 'last_name',
            'avatar_url', 
            'role_name', # Заменили 'role' (который был StringRelatedField) на 'role_name'
            'region_name',# Заменили 'region' на 'region_name'
            'phone_number', 'is_staff',
            'role_permissions' # Добавили права
        )
        read_only_fields = ('email', 'is_staff', 'role_name', 'region_name', 'avatar_url', 'role_permissions')

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


class AnimalNestedManageSerializer(serializers.ModelSerializer):
    species = serializers.PrimaryKeyRelatedField(queryset=Species.objects.all())
    breed = serializers.PrimaryKeyRelatedField(queryset=Breed.objects.all(), allow_null=True, required=False)
    color = serializers.PrimaryKeyRelatedField(queryset=AnimalColor.objects.all(), allow_null=True, required=False)
    gender = serializers.ChoiceField(choices=Animal.GENDER_CHOICES, allow_null=True, required=False)

    class Meta:
        model = Animal
        fields = ['name', 'birth_date', 'species', 'breed', 'color', 'gender']

class AdPhotoManageSerializer(serializers.ModelSerializer):
    # Для загрузки новых фото
    # image = serializers.ImageField(required=True) # Используется в AdManageSerializer
    class Meta:
        model = AdPhoto
        fields = ['id', 'image'] # 'id' для существующих фото, 'image' для новых


class AdvertisementManageSerializer(serializers.ModelSerializer):
    animal_data = AnimalNestedManageSerializer(write_only=True) # Вложенные данные для животного
    status = serializers.PrimaryKeyRelatedField(queryset=AdStatus.objects.all()) # ID статуса
    # Для загрузки нескольких фото. DRF не поддерживает вложенную запись для FileField/ImageField напрямую в many=True.
    # Будем обрабатывать загрузку фото отдельно во view или в методах create/update.
    # Либо использовать сторонние библиотеки типа drf-writable-nested.
    # Пока что сделаем загрузку фото через отдельный механизм или упрощенно.
    # Для простоты, пока не будем напрямую обрабатывать photos в этом сериализаторе,
    # а сделаем это во ViewSet или в методах create/update.
    # Либо, если фото загружаются отдельно после создания объявления:
    # photos = AdPhotoManageSerializer(many=True, read_only=True) # Только для чтения существующих

    # Для загрузки: будем ожидать список файлов в request.FILES с ключом 'photos_upload'
    # и список ID существующих фото для сохранения `existing_photo_ids`

    class Meta:
        model = Advertisement
        fields = [
            'id', 'title', 'description', 'status',
            'latitude', 'longitude',
            'animal_data', # Вложенные данные для создания/обновления животного
            # 'user' и 'publication_date' устанавливаются автоматически
        ]
        read_only_fields = ['id']

    def validate_status(self, value): # value здесь - это объект AdStatus
        user = self.context['request'].user
        # Разрешенные статусы для обычного пользователя при создании
        allowed_statuses_for_user = ["Потеряно", "Найдено", "Отдам в добрые руки"] # Пример
        
        # Если это создание нового объявления (self.instance is None)
        # И пользователь не админ/модератор
        if not self.instance and not (user.is_staff or (user.role and user.role.can_manage_any_advertisement)):
            if value.name not in allowed_statuses_for_user:
                raise serializers.ValidationError(f"Вы не можете установить статус '{value.name}'. Разрешенные статусы: {', '.join(allowed_statuses_for_user)}.")
        # При обновлении, если пользователь - владелец, но не модератор, он не должен мочь менять на "Активно" и т.п.
        # Эта логика может быть сложнее и зависит от ваших правил.
        # Например, владелец может поменять "Потеряно" на "Найдено владельцем".
        elif self.instance and self.instance.user == user and not (user.is_staff or (user.role and user.role.can_manage_any_advertisement)):
            # Здесь можно добавить логику, какие статусы владелец может менять на какие
            # if value.name in ["Активно", "Отклонено", "На модерации"] and self.instance.status.name != value.name:
            #     raise serializers.ValidationError("Вы не можете установить этот статус.")
            pass # Пока просто пропускаем, если это обновление владельцем

        return value

    def create(self, validated_data):
        animal_data = validated_data.pop('animal_data')
        
        # Создаем или получаем животное
        # Здесь можно добавить логику поиска существующего животного, если нужно
        # Пока что всегда создаем новое для простоты примера.
        # Если бы у нас был animal_id в validated_data, мы бы обновляли существующее.
        animal = Animal.objects.create(**animal_data)
        
        validated_data['animal'] = animal
        validated_data['user'] = self.context['request'].user
        advertisement = Advertisement.objects.create(**validated_data)
        
        # Обработка загруженных фото (если они передаются вместе с созданием объявления)
        # Этот код нужно будет адаптировать под то, как фото передаются с фронтенда
        uploaded_photos = self.context['request'].FILES.getlist('photos_upload') # Пример ключа
        for photo_file in uploaded_photos:
            AdPhoto.objects.create(advertisement=advertisement, image=photo_file)
            
        return advertisement

    def update(self, instance, validated_data):
        # Обрабатываем поля животного отдельно
        animal_instance = instance.animal
        print(validated_data, 'animal_name' in validated_data)
        
        # validated_data УЖЕ будет содержать объекты Species, Breed и т.д. 
        # для полей animal_species, animal_breed, если они были в запросе и прошли валидацию
        # PrimaryKeyRelatedField преобразует ID из запроса в экземпляры моделей.
        animal_data = validated_data.pop('animal_data', None)
        # Обновляем поля животного, если они есть в validated_data
        if 'name' in animal_data:
            animal_instance.name = animal_data.pop('name')
        if 'birth_date' in animal_data:
            animal_instance.birth_date = animal_data.pop('birth_date')
        if 'species' in animal_data: # Здесь validated_data['animal_species'] это объект Species
            animal_instance.species = animal_data.pop('species')
        if 'breed' in animal_data:   # Здесь validated_data['animal_breed'] это объект Breed
            animal_instance.breed = animal_data.pop('breed')
        if 'color' in animal_data:   # ... объект AnimalColor
            animal_instance.color = animal_data.pop('color')
        if 'gender' in animal_data:  # ... объект AnimalGender
            animal_instance.gender = animal_data.pop('gender')
        
        animal_instance.save() # Сохраняем изменения в животном
        
        # Обновляем остальные поля объявления (те, что остались в validated_data)
        # super().update() вызовет instance.save() для объявления
        instance = super().update(instance, validated_data) 

        # ... (обработка фото как раньше) ...
        uploaded_photos = self.context['request'].FILES.getlist('photos_upload')
        delete_photo_ids_str = self.context['request'].POST.getlist('delete_photos')
        if delete_photo_ids_str:
            AdPhoto.objects.filter(advertisement=instance, id__in=map(int, delete_photo_ids_str)).delete()
        for photo_file in uploaded_photos:
            AdPhoto.objects.create(advertisement=instance, image=photo_file)
            
        return instance



class BreedSerializer(serializers.ModelSerializer):
    # species = serializers.StringRelatedField() # Если хотите имя вида
    species_id = serializers.IntegerField(source='species.id') # Или просто ID вида

    class Meta:
        model = Breed
        fields = ['id', 'name', 'species_id'] # Или 'species' вместо 'species_id'