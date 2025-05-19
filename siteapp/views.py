# siteapp/views_api.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics, filters # generics и filters добавлены
from rest_framework.pagination import PageNumberPagination # Добавлено для пагинации
from django_filters.rest_framework import DjangoFilterBackend

from .models import Advertisement, Article, AdStatus, ArticleCategory, Region, Species, AnimalColor, AnimalGender
from .serializers import (
    HomePageAdSerializer, HomePageArticleSerializer,
    ArticleListSerializer, ArticleCategorySerializer, ArticleDetailSerializer,
    AdvertisementListSerializer, RegionSerializer, SpeciesSerializer, AdStatusSerializer,
    AnimalColorSerializer, AnimalGenderSerializer
)

from .filters import AdvertisementFilter, AGE_CHOICES

class HomePageDataAPIView(APIView):
    """
    API View для получения данных, необходимых для главной страницы.
    Включает:
    - Последние активные объявления (например, 4)
    - Последнюю "большую" статью
    - Несколько последних "маленьких" статей (например, 3)
    """
    def get(self, request, *args, **kwargs):
        # --- Последние объявления ---
        try:
            active_status, _ = AdStatus.objects.get_or_create(name="Активно") # Используем get_or_create для надежности
            recent_ads = Advertisement.objects.filter(status=active_status) \
                             .select_related('animal__species', 'user__region') \
                             .prefetch_related('photos') \
                             .order_by('-publication_date')[:4]
        except Exception as e:
            # Логирование ошибки e
            print(f"Error fetching recent ads: {e}") # Просто print для примера
            recent_ads = Advertisement.objects.none()


        # --- Статьи ---
        # prefetch_related('categories') добавлен для оптимизации
        latest_articles = Article.objects.select_related('author').prefetch_related('categories').order_by('-publication_date')

        main_article_qs = latest_articles[:1]
        side_articles_qs = latest_articles[1:3]

        serializer_context = {'request': request}

        recent_ads_serializer = HomePageAdSerializer(recent_ads, many=True, context=serializer_context)
        main_article_serializer = HomePageArticleSerializer(main_article_qs, many=True, context=serializer_context)
        side_articles_serializer = HomePageArticleSerializer(side_articles_qs, many=True, context=serializer_context)

        data = {
            'recent_ads': recent_ads_serializer.data,
            'main_article': main_article_serializer.data[0] if main_article_serializer.data else None,
            'side_articles': side_articles_serializer.data,
        }
        return Response(data, status=status.HTTP_200_OK)

# Класс пагинации
class StandardResultsSetPagination(PageNumberPagination):
    page_size = 9 # Количество статей на странице (3x3 сетка в макете)
    page_size_query_param = 'page_size' # Позволяет клиенту переопределить page_size
    max_page_size = 30

class ArticleListAPIView(generics.ListAPIView):
    serializer_class = ArticleListSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter] # Подключаем SearchFilter
    search_fields = ['title', 'content'] # По каким полям будет происходить поиск

    def get_queryset(self):
        queryset = Article.objects.select_related('author') \
                                  .prefetch_related('categories') \
                                  .filter(publication_date__isnull=False) \
                                  .order_by('-publication_date')

        category_slug = self.request.query_params.get('category', None)
        if category_slug and category_slug != 'all': # 'all' для сброса фильтра по категории
            queryset = queryset.filter(categories__slug=category_slug)
        return queryset

class ArticleCategoryListAPIView(generics.ListAPIView):
    queryset = ArticleCategory.objects.all().order_by('name')
    serializer_class = ArticleCategorySerializer
    pagination_class = None

class ArticleDetailAPIView(generics.RetrieveAPIView):
    queryset = Article.objects.select_related('author').all() # prefetch_related('categories') если они нужны
    serializer_class = ArticleDetailSerializer
    lookup_field = 'id' # Используем ID для поиска статьи

class AdsPageNumberPagination(PageNumberPagination):
    page_size = 12 # По 3 в ряд, 4 ряда = 12 (или сколько вам нужно)
    page_size_query_param = 'page_size'
    max_page_size = 48

class AdvertisementListAPIView(generics.ListAPIView):
    serializer_class = AdvertisementListSerializer
    pagination_class = AdsPageNumberPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter] # Добавляем OrderingFilter
    filterset_class = AdvertisementFilter # Используем наш FilterSet
    
    # Поля для сортировки. На фронте можно будет передавать ?ordering=publication_date или ?ordering=-publication_date
    ordering_fields = ['publication_date', 'animal__name'] 
    ordering = ['-publication_date'] # Сортировка по умолчанию

    def get_queryset(self):
        # Оптимизируем запросы
        return Advertisement.objects.select_related(
            'animal__species', 'animal__breed', 'animal__color', 'animal__gender',
            'user__region', 'status'
        ).prefetch_related('photos').all()


class FilterOptionsAPIView(APIView):
    """
    Возвращает списки возможных значений для фильтров.
    """
    def get(self, request, *args, **kwargs):
        data = {
            'regions': RegionSerializer(Region.objects.all(), many=True).data,
            'species': SpeciesSerializer(Species.objects.all(), many=True).data,
            'ad_statuses': AdStatusSerializer(AdStatus.objects.all(), many=True).data, # Это "Тип объявления"
            'colors': AnimalColorSerializer(AnimalColor.objects.all(), many=True).data,
            'genders': AnimalGenderSerializer(AnimalGender.objects.all(), many=True).data,
            'age_categories': [{'value': choice[0], 'label': choice[1]} for choice in AGE_CHOICES],
            # Добавьте сюда другие опции, если они появятся
        }
        return Response(data, status=status.HTTP_200_OK)