from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics, filters, permissions, viewsets, parsers
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count


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
)

from .filters import AdvertisementFilter, AGE_CHOICES
from .permissions import (
    IsOwnerOrAdminOrModeratorForComment,
    CanManageArticles,
    CanManageAdvertisements,
)


class HomePageDataAPIView(APIView):
    """
    API View для получения данных, необходимых для главной страницы.
    Включает:
    - Последние активные объявления (например, 4)
    - Последнюю "большую" статью
    - Несколько последних "маленьких" статей (например, 3)
    """

    def get(self, request, *args, **kwargs):

        try:
            active_status, _ = AdStatus.objects.get_or_create(name="Активно")
            recent_ads_qs = Advertisement.active_ads.active()
            recent_ads = (
                recent_ads_qs.exclude(status__name="Требует модерации")
                .select_related("animal__species", "user__region")
                .prefetch_related("photos")
                .order_by("-publication_date")[:4]
            )
        except Exception as e:

            print(f"Error fetching recent ads: {e}")
            recent_ads = Advertisement.objects.none()

        latest_articles = (
            Article.objects.select_related("author")
            .prefetch_related("categories")
            .order_by("-publication_date")
        )

        main_article_qs = latest_articles[:1]
        side_articles_qs = latest_articles[1:3]

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

        data = {
            "recent_ads": recent_ads_serializer.data,
            "main_article": (
                main_article_serializer.data[0]
                if main_article_serializer.data
                else None
            ),
            "side_articles": side_articles_serializer.data,
        }
        return Response(data, status=status.HTTP_200_OK)


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 9
    page_size_query_param = "page_size"
    max_page_size = 30


class ArticleListAPIView(generics.ListAPIView):
    serializer_class = ArticleListSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ["title", "content"]

    def get_queryset(self):
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
    queryset = ArticleCategory.objects.all().order_by("name")
    serializer_class = ArticleCategorySerializer
    pagination_class = None


class AdsPageNumberPagination(PageNumberPagination):
    page_size = 12
    page_size_query_param = "page_size"
    max_page_size = 48


class AdvertisementListAPIView(generics.ListAPIView):
    serializer_class = AdvertisementListSerializer
    pagination_class = AdsPageNumberPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = AdvertisementFilter

    ordering_fields = ["publication_date", "animal__name"]
    ordering = ["-publication_date"]

    def get_queryset(self):

        return (
            Advertisement.objects.select_related(
                "animal__species",
                "animal__breed",
                "animal__color",
                "user__region",
                "status",
            )
            .prefetch_related("photos")
            .all()
        )


class FilterOptionsAPIView(APIView):
    """
    Возвращает списки возможных значений для фильтров.
    """

    def get(self, request, *args, **kwargs):
        gender_options = [
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
        }
        return Response(data, status=status.HTTP_200_OK)


class AdvertisementDetailAPIView(generics.RetrieveAPIView):
    queryset = (
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
    lookup_field = "id"


class AdResponseCreateAPIView(generics.CreateAPIView):
    queryset = AdResponse.objects.all()
    serializer_class = AdResponseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        advertisement_id = self.kwargs.get("ad_id")
        advertisement = generics.get_object_or_404(Advertisement, pk=advertisement_id)
        serializer.save(user=self.request.user, advertisement=advertisement)


class AdResponseDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = AdResponse.objects.select_related("user", "user__role").all()
    serializer_class = AdResponseSerializer
    permission_classes = [IsOwnerOrAdminOrModeratorForComment]
    lookup_url_kwarg = "response_id"

    def get_queryset(self):

        ad_id = self.kwargs.get("ad_id")
        return super().get_queryset().filter(advertisement_id=ad_id)


class ArticleListCreateAPIView(generics.ListCreateAPIView):
    queryset = (
        Article.objects.select_related("author")
        .prefetch_related("categories")
        .order_by("-publication_date")
    )
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    search_fields = ["title", "content", "author__display_name"]
    ordering_fields = ["publication_date", "title"]
    ordering = ["-publication_date"]
    pagination_class = StandardResultsSetPagination
    permission_classes = [CanManageArticles]

    def get_queryset(self):
        queryset = (
            Article.objects.annotate(comments_count=Count("comments"))
            .select_related("author")
            .prefetch_related("categories")
            .order_by("-publication_date")
        )

        category_slug = self.request.query_params.get("category", None)
        if category_slug and category_slug != "all":
            queryset = queryset.filter(categories__slug=category_slug)
        return queryset

    def get_serializer_class(self):
        if self.request.method == "POST":
            return ArticleManageSerializer
        return ArticleListSerializer


class ArticleRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = (
        Article.objects.select_related("author")
        .prefetch_related("categories", "comments__user")
        .all()
    )
    permission_classes = [CanManageArticles]
    lookup_field = "id"

    def get_serializer_class(self):
        if self.request.method in ["PUT", "PATCH"]:
            return ArticleManageSerializer
        return ArticleDetailSerializer


class ArticleCommentListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        article_id = self.kwargs.get("article_id")
        return (
            Comment.objects.filter(article_id=article_id)
            .select_related("user")
            .order_by("-date_created")
        )

    def perform_create(self, serializer):
        article_id = self.kwargs.get("article_id")
        article = generics.get_object_or_404(Article, pk=article_id)
        serializer.save(user=self.request.user, article=article)


class ArticleCommentRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsOwnerOrAdminOrModeratorForComment]
    lookup_url_kwarg = "comment_id"

    def get_queryset(self):
        article_id = self.kwargs.get("article_id")
        return Comment.objects.filter(article_id=article_id).select_related("user")


class AdvertisementViewSet(viewsets.ModelViewSet):
    queryset = (
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

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = AdvertisementFilter

    pagination_class = AdsPageNumberPagination
    permission_classes = [CanManageAdvertisements]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser]

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return AdvertisementManageSerializer
        elif self.action == "retrieve":
            return AdvertisementDetailSerializer
        return AdvertisementListSerializer


class BreedListAPIView(generics.ListAPIView):
    queryset = Breed.objects.select_related("species").all()
    serializer_class = BreedSerializer

    permission_classes = [permissions.AllowAny]
