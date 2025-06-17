from typing import Dict, List, Type, Any, Optional
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics, filters, permissions, viewsets, parsers
from rest_framework.pagination import PageNumberPagination
from rest_framework.serializers import BaseSerializer, ModelSerializer, ValidationError
from rest_framework.permissions import BasePermission
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Avg, QuerySet
from django.db.models.base import ModelBase
from rest_framework.parsers import BaseParser

from .models import (
    Advertisement,
    Article,
    AdStatus,
    ArticleCategory,
    Region,
    Species,
    AnimalColor,
    AdResponse,
    Comment,
    Breed,
    Animal,
    AdvertisementRating,
    User,
    Role,
)
from .serializers import (
    HomePageAdSerializer,
    HomePageArticleSerializer,
    ArticleListSerializer,
    ArticleCategorySerializer,
    ArticleDetailSerializer,
    AdvertisementListSerializer,
    RegionSerializer,
    SpeciesSerializer,
    AdStatusSerializer,
    AnimalColorSerializer,
    AdvertisementDetailSerializer,
    AdResponseSerializer,
    ArticleManageSerializer,
    CommentSerializer,
    AdvertisementManageSerializer,
    BreedSerializer,
    RegionActivitySerializer,
    AdvertisementRatingSerializer,
    RoleSerializer,
    ProfileSerializer,
    ProfileUpdateSerializer,
    AdminProfileUpdateSerializer,
    UserAdminSerializer,
)

from .filters import AdvertisementFilter, AGE_CHOICES
from .permissions import (
    IsOwnerOrAdminOrModeratorForComment,
    CanManageArticles,
    CanManageAdvertisements,
    IsOwnerOrAdminOrReadOnly,
    IsOwnerOrAdmin,
)


class HomePageDataAPIView(APIView):
    """
    API View для получения данных, необходимых для главной страницы.
    Возвращает:
    - Последние активные объявления (например, 4)
    - Последнюю "большую" статью
    - Несколько последних "маленьких" статей (например, 3)
    - 5 регионов с наибольшим количеством объявлений
    """

    def get(self, request, *args, **kwargs) -> Response:
        recent_ads: QuerySet[Advertisement] = Advertisement.objects.none()
        main_article: QuerySet[Article] = Article.objects.none()
        side_articles: QuerySet[Article] = Article.objects.none()
        top_regions: List[Dict[str, Any]] = []

        try:
            active_status, _ = AdStatus.objects.get_or_create(name="Активно")
            recent_ads_qs = Advertisement.objects.filter(status=active_status)
            recent_ads = (
                recent_ads_qs.select_related("animal__species", "user__region")
                .prefetch_related("photos")
                .order_by("-publication_date")[:4]
            )
        except Exception as e:
            print(f"Error fetching recent ads: {e}")

        latest_articles = (
            Article.objects.select_related("author")
            .prefetch_related("categories")
            .order_by("-publication_date")
        )

        main_article_qs = latest_articles[:1]
        side_articles_qs = latest_articles[1:3]

        serializer_context = {"request": request}

        try:
            active_status = AdStatus.objects.get(name="Активно")
            region_activity = (
                Advertisement.objects.filter(
                    status=active_status, user__region__isnull=False
                )
                .values("user__region__id", "user__region__name")
                .annotate(ad_count=Count("id", distinct=True))
                .order_by("-ad_count")[:5]
            )
            top_regions = [
                {
                    "region__id": r["user__region__id"],
                    "region__name": r["user__region__name"],
                    "ad_count": r["ad_count"],
                }
                for r in region_activity
            ]

        except AdStatus.DoesNotExist:
            print("WARNING: AdStatus 'Активно' not found for top regions widget.")
        except Exception as e:
            print(f"Error fetching top regions: {e}")

        serializer_context = {"request": request}

        recent_ads_serializer = HomePageAdSerializer(
            recent_ads, many=True, context=serializer_context
        )
        main_article_serializer = HomePageArticleSerializer(
            main_article_qs, many=True, context=serializer_context
        )
        side_articles_serializer = HomePageArticleSerializer(
            side_articles_qs, many=True, context=serializer_context
        )
        top_regions_serializer = RegionActivitySerializer(
            top_regions, many=True, context=serializer_context
        )

        data = {
            "recent_ads": recent_ads_serializer.data,
            "main_article": (
                main_article_serializer.data[0]
                if main_article_serializer.data
                else None
            ),
            "side_articles": side_articles_serializer.data,
            "top_regions": top_regions_serializer.data,  # <-- Новые данные
        }
        return Response(data, status=status.HTTP_200_OK)


class StandardResultsSetPagination(PageNumberPagination):
    """
    Стандартная пагинация - по 9 элементов на странице.

    Параметры:
        page_size (int): количество элементов на странице. Максимум - 30.
        page_size_query_param (str): параметр запроса для page_size. По умолчанию "page_size".
    """

    page_size: int = 9
    page_size_query_param: str = "page_size"
    max_page_size: int = 30


class ArticleListAPIView(generics.ListAPIView):
    """
    Возвращает список статей.

    Параметры:
        category (str): Слаг категории, по которой фильтровать статьи.
    """

    serializer_class = ArticleListSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ["title", "content"]

    def get_queryset(self) -> QuerySet[Article]:
        queryset = (
            Article.objects.select_related("author")
            .prefetch_related("categories")
            .filter(publication_date__isnull=False)
            .order_by("-publication_date")
        )

        category_slug = self.request.query_params.get("category", None)
        if category_slug and category_slug != "all":
            queryset = queryset.filter(categories__slug=category_slug)
        return queryset


class ArticleCategoryListAPIView(generics.ListAPIView):
    """
    Возвращает список категорий статей.
    """

    queryset: QuerySet[ArticleCategory] = ArticleCategory.objects.all().order_by("name")
    serializer_class = ArticleCategorySerializer
    pagination_class = None


class AdsPageNumberPagination(PageNumberPagination):
    """
    Пагинатор для объявлений.
    """

    page_size: int = 12
    page_size_query_param: str = "page_size"
    max_page_size: int = 48


class FilterOptionsAPIView(APIView):
    """
    Возвращает списки возможных значений для фильтров.
    """

    def get(self, request, *args, **kwargs) -> Response:
        gender_options: List[Dict[str, str]] = [
            {"value": choice[0], "label": str(choice[1])}
            for choice in Animal.GENDER_CHOICES
        ]

        data = {
            "regions": RegionSerializer(Region.objects.all(), many=True).data,
            "species": SpeciesSerializer(Species.objects.all(), many=True).data,
            "ad_statuses": AdStatusSerializer(AdStatus.objects.all(), many=True).data,
            "colors": AnimalColorSerializer(AnimalColor.objects.all(), many=True).data,
            "genders": gender_options,
            "age_categories": [
                {"value": choice[0], "label": choice[1]} for choice in AGE_CHOICES
            ],
            "breeds": BreedSerializer(
                Breed.objects.select_related("species").order_by("name"), many=True
            ).data,
        }
        return Response(data, status=status.HTTP_200_OK)


class AdvertisementDetailAPIView(generics.RetrieveAPIView):
    """
    Возвращает подробную информацию об объявлении.

    retrieve:
    Возвращает подробную информацию об объявлении.
    """

    queryset: QuerySet[Advertisement] = (
        Advertisement.objects.select_related(
            "animal__species",
            "animal__breed",
            "animal__color",
            "user__region",
            "user__role",
            "status",
        )
        .prefetch_related("photos", "responses__user__role", "responses__user__region")
        .all()
    )
    serializer_class = AdvertisementDetailSerializer
    lookup_field: str = "id"


class AdResponseCreateAPIView(generics.CreateAPIView):
    """
    Представление для создания откликов к объявлениям.

    create:
    Создает отклик к объявлению.

    permission_classes:
    IsAuthenticated - разрешает создание только авторизованным.
    """

    queryset: QuerySet[AdResponse] = AdResponse.objects.all()
    serializer_class = AdResponseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer: AdResponseSerializer) -> None:
        """
        Выполняет создание отклика к объявлению.

        :param serializer: сериализатор для создания отклика
        """
        advertisement_id = self.kwargs.get("ad_id")
        advertisement = generics.get_object_or_404(Advertisement, pk=advertisement_id)
        serializer.save(user=self.request.user, advertisement=advertisement)


class AdResponseDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    Представление для управления отдельными откликами к объявлениям.

    retrieve:
    Возвращает отклик к объявлению.

    update:
    Обновляет отклик к объявлению.

    destroy:
    Удаляет отклик к объявлению.

    permission_classes:
    IsOwnerOrAdminOrModeratorForComment - разрешает:
    - чтение всем;
    - создание: только авторизованным;
    - изменение: только автору, администратору, модератору;
    - удаление: только автору, администратору, модератору.
    """

    queryset: QuerySet[AdResponse] = AdResponse.objects.select_related(
        "user", "user__role"
    ).all()
    serializer_class = AdResponseSerializer
    permission_classes = [IsOwnerOrAdminOrModeratorForComment]
    lookup_url_kwarg = "response_id"

    def get_queryset(self) -> QuerySet[AdResponse]:
        ad_id = self.kwargs.get("ad_id")
        return super().get_queryset().filter(advertisement_id=ad_id)


class ArticleListCreateAPIView(generics.ListCreateAPIView):
    """
    Представление для получения списка статей и создания новой статьи.

    list:
    Возвращает список статей.

    create:
    Создает новую статью.
    """

    queryset: QuerySet = (
        Article.objects.select_related("author")
        .prefetch_related("categories")
        .order_by("-publication_date")
    )
    filter_backends: list = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    search_fields: list = ["title", "content", "author__display_name"]
    ordering_fields: list = ["publication_date", "title"]
    ordering: list = ["-publication_date"]
    pagination_class = StandardResultsSetPagination
    permission_classes: list = [CanManageArticles]

    def get_queryset(self) -> QuerySet:
        """
        Возвращает набор запросов статей, отфильтрованный по категории, если она указана.
        """
        queryset: QuerySet = (
            Article.objects.annotate(comments_count=Count("comments"))
            .select_related("author")
            .prefetch_related("categories")
            .order_by("-publication_date")
        )

        category_slug: Optional[str] = self.request.query_params.get("category", None)
        if category_slug and category_slug != "all":
            queryset = queryset.filter(categories__slug=category_slug)
        return queryset

    def get_serializer_class(self) -> Type[BaseSerializer]:
        """
        Возвращает класс сериализатора в зависимости от метода запроса.
        """
        if self.request.method == "POST":
            return ArticleManageSerializer
        return ArticleListSerializer


class ArticleRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    Представление для деталей, обновления и удаления статьи.

    retrieve:
    Возвращает детали статьи.

    update:
    Обновляет статью. Доступно только авторизованным пользователям, которые имеют права на редактирование статей.

    partial_update:
    Частично обновляет статью. Доступно только авторизованным пользователям, которые имеют права на редактирование статей.

    destroy:
    Удаляет статью. Доступно только авторизованным пользователям, которые имеют права на удаление статей.
    """

    queryset = (
        Article.objects.select_related("author")
        .prefetch_related("categories", "comments__user")
        .all()
    )
    permission_classes: List[Type[permissions.BasePermission]] = [CanManageArticles]
    lookup_field: str = "id"

    def get_serializer_class(self) -> Type[ModelSerializer]:
        if self.request.method in ["PUT", "PATCH"]:
            return ArticleManageSerializer
        return ArticleDetailSerializer


class ArticleCommentListCreateAPIView(generics.ListCreateAPIView):
    """
    Представление для списка и создания комментариев к статьям.

    list:
    Возвращает список комментариев к статье.

    create:
    Создает новый комментарий к статье. Доступно только авторизованным пользователям.
    """

    serializer_class: Type[CommentSerializer] = CommentSerializer
    permission_classes: List[Type[permissions.BasePermission]] = [
        permissions.IsAuthenticatedOrReadOnly
    ]

    def get_queryset(self) -> QuerySet[Comment]:
        article_id: int = self.kwargs.get("article_id")
        return (
            Comment.objects.filter(article_id=article_id)
            .select_related("user")
            .order_by("-date_created")
        )

    def perform_create(self, serializer: CommentSerializer) -> None:
        article_id: int = self.kwargs.get("article_id")
        article: Article = generics.get_object_or_404(Article, pk=article_id)
        serializer.save(user=self.request.user, article=article)


class ArticleCommentRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    Представление для управления отдельными комментариями к статьям.

    retrieve:
    Возвращает комментарий к статье.

    update:
    Обновляет комментарий к статье.

    destroy:
    Удаляет комментарий к статье.

    permission_classes:
    IsOwnerOrAdminOrModeratorForComment - разрешает:
    - чтение всем;
    - создание: только авторизованным;
    - изменение: только автору, администратору, модератору;
    - удаление: только автору, администратору, модератору.
    """

    serializer_class = CommentSerializer
    permission_classes = [IsOwnerOrAdminOrModeratorForComment]
    lookup_url_kwarg = "comment_id"

    def get_queryset(self) -> QuerySet:
        article_id = self.kwargs.get("article_id")
        return Comment.objects.filter(article_id=article_id).select_related("user")


class AdvertisementViewSet(viewsets.ModelViewSet):
    """
    Представление для управления объявлениями.

    list:
    Возвращает список всех объявлений.

    retrieve:
    Возвращает детали указанного объявления.

    create:
    Создает новое объявление.

    update:
    Обновляет указанное объявление.

    partial_update:
    Частично обновляет указанное объявление.

    destroy:
    Удаляет указанное объявление.
    """

    queryset: QuerySet[Advertisement] = (
        Advertisement.objects.select_related(
            "animal__species",
            "animal__breed",
            "animal__color",
            "user__region",
            "user__role",
            "status",
        )
        .prefetch_related("photos", "responses__user")
        .order_by("-publication_date")
    )

    filter_backends: list = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class: Type[AdvertisementFilter] = AdvertisementFilter

    pagination_class: Type[PageNumberPagination] = AdsPageNumberPagination
    permission_classes: List[Type[BasePermission]] = [CanManageAdvertisements]
    parser_classes: List[Type[BaseParser]] = [
        parsers.MultiPartParser,
        parsers.FormParser,
        parsers.JSONParser,
    ]

    def get_queryset(self) -> QuerySet[Advertisement]:
        """
        Возвращает набор данных объявлений с аннотациями по количеству комментариев и среднему рейтингу.

        :return: Запрос с аннотациями.
        """
        queryset: QuerySet[Advertisement] = (
            Advertisement.objects.annotate(
                comments_count=Count("responses", distinct=True),
                average_rating=Avg("ratings__rating"),
                rating_count=Count("ratings", distinct=True),
            )
            .select_related(
                "animal__species",
                "animal__breed",
                "animal__color",
                "user__region",
                "user__role",
                "status",
            )
            .prefetch_related(
                "photos",
            )
            .order_by("-publication_date")
        )

        if self.action == "retrieve":
            queryset = queryset.prefetch_related("responses__user__role")

        return queryset

    def get_serializer_class(self) -> Type[BaseSerializer]:
        """
        Возвращает класс сериализатора в зависимости от действия.

        :return: Класс сериализатора.
        """
        if self.action in ["create", "update", "partial_update"]:
            return AdvertisementManageSerializer
        elif self.action == "retrieve":
            return AdvertisementDetailSerializer
        return AdvertisementListSerializer


class BreedListAPIView(generics.ListAPIView):
    """
    Возвращает список пород.

    """

    queryset: QuerySet[Breed] = Breed.objects.select_related("species").all()
    serializer_class: Type[BreedSerializer] = BreedSerializer

    permission_classes = [permissions.AllowAny]


class AdvertisementRatingViewSet(viewsets.ModelViewSet):
    """
    Endpoint для работы с оценками объявлений.

    list:
    Возвращает список всех оценок.

    retrieve:
    Возвращает оценку указанного объявления.

    create:
    Создает оценку для указанного объявления.

    update:
    Обновляет оценку указанного объявления.

    partial_update:
    Частично обновляет оценку указанного объявления.

    destroy:
    Удаляет оценку указанного объявления.
    """

    queryset: QuerySet[AdvertisementRating] = (
        AdvertisementRating.objects.select_related("user", "advertisement").all()
    )
    serializer_class = AdvertisementRatingSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["advertisement", "user"]
    pagination_class = None

    def perform_create(self, serializer: AdvertisementRatingSerializer) -> None:
        """
        Создает новую оценку для объявления, если пользователь еще не оставлял оценку.

        :param serializer: Сериализатор AdvertisementRatingSerializer с валидированными данными.
        :raises serializers.ValidationError: Если пользователь уже оставил оценку для данного объявления.
        """
        advertisement_id: int = serializer.validated_data.get("advertisement").id
        user = self.request.user

        if AdvertisementRating.objects.filter(
            advertisement_id=advertisement_id, user=user
        ).exists():
            raise ValidationError("Вы уже оставили оценку для этого объявления.")

        serializer.save(user=user)

    def get_permissions(self) -> List[permissions.BasePermission]:
        """
        Возвращает список разрешений для текущего действия.

        list, retrieve:
        Позволяет доступ всем пользователям.

        create:
        Позволяет доступ всем аутентифицированным пользователям.

        update, partial_update, destroy:
        Позволяет доступ владельцу или администратору.
        """
        if self.action in ["list", "retrieve"]:
            permission_classes = [permissions.AllowAny]
        elif self.action == "create":
            permission_classes = [permissions.IsAuthenticated]
        elif self.action in ["update", "partial_update", "destroy"]:
            permission_classes = [IsOwnerOrAdminOrReadOnly]
        else:
            permission_classes = [permissions.IsAdminUser]
        return [permission() for permission in permission_classes]


class ProfileViewSet(viewsets.ModelViewSet):
    """
    Endpoint для работы с профилями пользователей.

    list:
    Возвращает список всех пользователей.

    retrieve:
    Возвращает полный профиль указанного пользователя.

    update:
    Обновляет профиль указанного пользователя.

    partial_update:
    Частично обновляет профиль указанного пользователя.

    destroy:
    Удаляет профиль указанного пользователя.
    """

    queryset = User.objects.all().select_related("region", "role")
    parser_classes = [parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser]
    lookup_field = "id"

    def get_serializer_class(self) -> Type[ModelSerializer]:
        """
        Возвращает класс сериализатора для указанного действия.

        retrieve:
        Возвращает полный профиль указанного пользователя.

        update:
        Обновляет профиль указанного пользователя.

        partial_update:
        Частично обновляет профиль указанного пользователя.
        """
        if self.action == "retrieve":
            return ProfileSerializer
        elif self.action in ["update", "partial_update"]:
            if self.request.user.is_staff:
                return AdminProfileUpdateSerializer
            return ProfileUpdateSerializer
        return ProfileSerializer

    def get_permissions(self) -> List[permissions.BasePermission]:
        """
        Возвращает список разрешений для текущего действия.

        retrieve:
        Позволяет доступ всем пользователям.

        update, partial_update:
        Позволяет доступ владельцу или администратору.

        destroy:
        Позволяет доступ только администратору.
        """
        if self.action == "retrieve":
            permission_classes = [permissions.AllowAny]
        elif self.action in ["update", "partial_update"]:
            permission_classes = [IsOwnerOrAdmin]
        elif self.action == "destroy":
            permission_classes = [permissions.IsAdminUser]
        else:
            permission_classes = [permissions.IsAdminUser]
        return [permission() for permission in permission_classes]

    def update(self, request, *args, **kwargs) -> Response:
        """
        Кастомный метод обновления.
        После успешного обновления возвращает полный профиль через ProfileSerializer.
        """
        partial = kwargs.pop("partial", False)
        instance = self.get_object()

        update_serializer = self.get_serializer(
            instance, data=request.data, partial=partial
        )
        update_serializer.is_valid(raise_exception=True)
        self.perform_update(update_serializer)

        if getattr(instance, "_prefetched_objects_cache", None):
            instance = self.get_object()

        view_serializer = ProfileSerializer(
            instance, context=self.get_serializer_context()
        )

        return Response(view_serializer.data)

    def retrieve(self, request, *args, **kwargs) -> Response:
        """
        Возвращает полный профиль указанного пользователя.
        """
        instance = self.get_object()
        user_serializer = self.get_serializer(instance)
        user_ads = (
            Advertisement.objects.filter(user=instance)
            .select_related("animal__species", "status")
            .prefetch_related("photos")
            .order_by("-publication_date")[:12]
        )
        ads_serializer = AdvertisementListSerializer(
            user_ads, many=True, context={"request": request}
        )
        data = {"user": user_serializer.data, "advertisements": ads_serializer.data}
        return Response(data, status=status.HTTP_200_OK)


class RoleListAPIView(generics.ListAPIView):
    """
    Возвращает список всех ролей (названия и id).
    """

    queryset: QuerySet[Role] = Role.objects.all().order_by("name")

    serializer_class = RoleSerializer
    permission_classes = [permissions.IsAdminUser]
    pagination_class = None


class AdminPageNumberPagination(PageNumberPagination):
    """
    Кастомная пагинация для административных API (например, UserAdminViewSet).
    """

    page_size: int = 15
    page_size_query_param: str = "page_size"
    max_page_size: int = 100


class UserAdminViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet для управления пользователями в админ-панели.

    Доступно только для персонала (is_staff).
    Предоставляет список пользователей с поиском и фильтрацией.

    Может быть использован для просмотра, поиска, фильтрации и сортировки пользователей.
    """

    queryset: QuerySet[User] = (
        User.objects.all().select_related("role", "region").order_by("-date_joined")
    )
    serializer_class = UserAdminSerializer
    permission_classes = [permissions.IsAdminUser]
    pagination_class = AdminPageNumberPagination

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    search_fields = ["username", "email", "display_name", "first_name", "last_name"]
    filterset_fields = ["is_active", "is_staff", "role", "region"]
    ordering_fields = ["date_joined", "email", "username"]
    ordering = ["-date_joined"]
