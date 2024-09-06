from django.urls import path
from . import views
from django.conf.urls.static import static

urlpatterns = [
    path("", views.articles, name="articles"),
    path("articles/", views.articles, name="articles"),
    path("articles/search", views.articles_search, name="articles_search"),
    path("reviews/", views.reviews, name="reviews"),
    path("about/", views.about, name="about"),
]