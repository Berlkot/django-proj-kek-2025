# siteapp/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views_api import (
    HomePageDataAPIView,
    ArticleCategoryListAPIView,
    FilterOptionsAPIView,
    AdResponseCreateAPIView,
    AdResponseDetailAPIView,
    ArticleListCreateAPIView,
    ArticleRetrieveUpdateDestroyAPIView,
    ArticleCommentListCreateAPIView,
    ArticleCommentRetrieveUpdateDestroyAPIView,
    AdvertisementViewSet,
    BreedListAPIView,
    AdvertisementRatingViewSet 
)

router = DefaultRouter()
router.register(r"advertisements", AdvertisementViewSet, basename="advertisement")
router.register(r'advertisement-ratings', AdvertisementRatingViewSet, basename='advertisement-rating')

urlpatterns = [
    path("", include(router.urls)),
    path("homepage/", HomePageDataAPIView.as_view(), name="homepage_data_api"),
    path("articles/", ArticleListCreateAPIView.as_view(), name="article_list_create"),
    path(
        "articles/<int:id>/",
        ArticleRetrieveUpdateDestroyAPIView.as_view(),
        name="article_retrieve_update_destroy",
    ),
    path(
        "article-categories/",
        ArticleCategoryListAPIView.as_view(),
        name="article_category_list",
    ),
    path(
        "articles/<int:article_id>/comments/",
        ArticleCommentListCreateAPIView.as_view(),
        name="article_comment_list_create",
    ),
    path(
        "articles/<int:article_id>/comments/<int:comment_id>/",
        ArticleCommentRetrieveUpdateDestroyAPIView.as_view(),
        name="article_comment_retrieve_update_destroy",
    ),
    path("filter-options/", FilterOptionsAPIView.as_view(), name="filter_options"),
    path(
        "advertisements/<int:ad_id>/responses/",
        AdResponseCreateAPIView.as_view(),
        name="ad_response_create",
    ),
    path(
        "advertisements/<int:ad_id>/responses/<int:response_id>/",
        AdResponseDetailAPIView.as_view(),
        name="ad_response_detail",
    ),
    path("breeds/", BreedListAPIView.as_view(), name="breed_list"),
]
