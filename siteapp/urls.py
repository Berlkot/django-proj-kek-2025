# siteapp/urls_api.py
from django.urls import path
from .views import (
    HomePageDataAPIView, ArticleListAPIView, ArticleCategoryListAPIView, AdvertisementListAPIView, FilterOptionsAPIView,
    AdvertisementDetailAPIView, AdResponseCreateAPIView, AdResponseDetailAPIView,
    ArticleListCreateAPIView, ArticleRetrieveUpdateDestroyAPIView,
    ArticleCommentListCreateAPIView, ArticleCommentRetrieveUpdateDestroyAPIView,
) 

urlpatterns = [
    path('homepage/', HomePageDataAPIView.as_view(), name='homepage_data_api'),
    path('articles/', ArticleListAPIView.as_view(), name='article_list'),
    path('article-categories/', ArticleCategoryListAPIView.as_view(), name='article_category_list'),
    path('advertisements/', AdvertisementListAPIView.as_view(), name='advertisement_list'),
    path('filter-options/', FilterOptionsAPIView.as_view(), name='filter_options'),
    path('advertisements/<int:id>/', AdvertisementDetailAPIView.as_view(), name='advertisement_detail'),
    path('advertisements/<int:ad_id>/responses/', AdResponseCreateAPIView.as_view(), name='ad_response_create'),
    path('advertisements/<int:ad_id>/responses/<int:response_id>/', AdResponseDetailAPIView.as_view(), name='ad_response_detail'),
    path('articles/', ArticleListCreateAPIView.as_view(), name='article_list_create'),
    path('articles/<int:id>/', ArticleRetrieveUpdateDestroyAPIView.as_view(), name='article_retrieve_update_destroy'),
    path('articles/<int:article_id>/comments/', ArticleCommentListCreateAPIView.as_view(), name='article_comment_list_create'),
    path('articles/<int:article_id>/comments/<int:comment_id>/', ArticleCommentRetrieveUpdateDestroyAPIView.as_view(), name='article_comment_retrieve_update_destroy'),
]