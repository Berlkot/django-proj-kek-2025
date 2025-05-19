# siteapp/urls_api.py
from django.urls import path
from .views import (
    HomePageDataAPIView, ArticleListAPIView, ArticleCategoryListAPIView,
    ArticleDetailAPIView, AdvertisementListAPIView, FilterOptionsAPIView
) 

urlpatterns = [
    path('homepage/', HomePageDataAPIView.as_view(), name='homepage_data_api'),
    path('articles/', ArticleListAPIView.as_view(), name='article_list'),
    path('article-categories/', ArticleCategoryListAPIView.as_view(), name='article_category_list'),
    path('articles/<int:id>/', ArticleDetailAPIView.as_view(), name='article_detail'),
    path('advertisements/', AdvertisementListAPIView.as_view(), name='advertisement_list'),
    path('filter-options/', FilterOptionsAPIView.as_view(), name='filter_options'),
]