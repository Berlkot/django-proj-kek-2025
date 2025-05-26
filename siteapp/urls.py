# siteapp/urls.py
from django.urls import path, include # Добавьте include
from rest_framework.routers import DefaultRouter
from .views_api import (
    HomePageDataAPIView,
    # ArticleListAPIView, # Оставляем, если это ТОЛЬКО для списка статей без CRUD
    ArticleCategoryListAPIView,
    # AdvertisementListAPIView, # УДАЛЯЕМ - заменяется ViewSet
    FilterOptionsAPIView,
    # AdvertisementDetailAPIView, # УДАЛЯЕМ - заменяется ViewSet
    AdResponseCreateAPIView, AdResponseDetailAPIView,
    ArticleListCreateAPIView, ArticleRetrieveUpdateDestroyAPIView, # Это для статей, не объявлений
    ArticleCommentListCreateAPIView, ArticleCommentRetrieveUpdateDestroyAPIView,
    AdvertisementViewSet, # Наш ViewSet для объявлений,
    BreedListAPIView # Новый ViewSet для пород
)

router = DefaultRouter()
router.register(r'advertisements', AdvertisementViewSet, basename='advertisement') # Регистрируем ViewSet

urlpatterns = [
    path('', include(router.urls)),

    path('homepage/', HomePageDataAPIView.as_view(), name='homepage_data_api'),

    # Статьи (оставляем, так как для них отдельные View)
    path('articles/', ArticleListCreateAPIView.as_view(), name='article_list_create'),
    path('articles/<int:id>/', ArticleRetrieveUpdateDestroyAPIView.as_view(), name='article_retrieve_update_destroy'),
    path('article-categories/', ArticleCategoryListAPIView.as_view(), name='article_category_list'),

    # Комментарии к статьям
    path('articles/<int:article_id>/comments/', ArticleCommentListCreateAPIView.as_view(), name='article_comment_list_create'),
    path('articles/<int:article_id>/comments/<int:comment_id>/', ArticleCommentRetrieveUpdateDestroyAPIView.as_view(), name='article_comment_retrieve_update_destroy'),

    # Опции фильтров (если нужны отдельно)
    path('filter-options/', FilterOptionsAPIView.as_view(), name='filter_options'),

    # Комментарии к объявлениям (оставляем, если они не вложены в AdvertisementViewSet)
    path('advertisements/<int:ad_id>/responses/', AdResponseCreateAPIView.as_view(), name='ad_response_create'),
    path('advertisements/<int:ad_id>/responses/<int:response_id>/', AdResponseDetailAPIView.as_view(), name='ad_response_detail'),
    path('breeds/', BreedListAPIView.as_view(), name='breed_list'), # Новый URL
]