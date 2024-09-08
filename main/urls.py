from django.urls import path
from . import views
from django.conf.urls.static import static

urlpatterns = [
    path("", views.articles, name="articles"),
    path("articles/", views.articles, name="articles"),
    path("articles/search", views.articles_search, name="articles_search"),
    path("articles/<str:pk>", views.articles_info, name="articles_info"),
    path("reviews/", views.reviews, name="reviews"),
    path("reviews/search", views.reviews_search, name="reviews_search"),
    path("reviews/<str:pk>", views.reviews_info, name="reviews_info"),
    path("about/", views.about, name="about"),
]