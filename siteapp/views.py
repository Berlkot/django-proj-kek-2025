# siteapp/views_api.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Advertisement, Article, AdStatus
from .serializers import HomePageAdSerializer, HomePageArticleSerializer

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
            # Предположим, что статус "Активно" существует и имеет такое имя
            # или используйте ID, если он известен и статичен: AdStatus.objects.get(id=1)
            active_status = AdStatus.objects.get(name="Активно") # Замените "Активно" на ваш реальный статус
            recent_ads = Advertisement.objects.filter(status=active_status) \
                             .select_related('animal__species', 'user__region') \
                             .prefetch_related('photos') \
                             .order_by('-publication_date')[:4]
        except AdStatus.DoesNotExist:
            # Если статус "Активно" не найден, возвращаем пустой список объявлений
            # или обрабатываем ошибку иначе
            recent_ads = Advertisement.objects.none()
        except Exception as e:
            # Логирование ошибки e
            recent_ads = Advertisement.objects.none()


        # --- Статьи ---
        # Получаем последние статьи, самая новая будет "большой"
        latest_articles = Article.objects.select_related('author').order_by('-publication_date')

        main_article_qs = latest_articles[:1] # Первая (самая новая)
        side_articles_qs = latest_articles[1:4] # Следующие 3

        # Сериализация данных
        # Передаем 'request' в контекст для генерации полных URL изображений
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