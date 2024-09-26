"""
URL configuration for fungalmaterials project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# from debug_toolbar.toolbar import debug_toolbar_urls
from django.contrib import admin
from django.urls import path, include
from django.urls.converters import register_converter

from fungalmaterials import views
from fungalmaterials.converters import FullPathConverter

register_converter(FullPathConverter, 'fullpath')

urlpatterns = ([
                  path('admin/', admin.site.urls),
                  path("", views.articles, name="articles"),
                  path("articles/", views.articles, name="articles"),
                  path("articles/search", views.articles_search, name="articles_search"),
                  path("articles/<str:pk>", views.articles_info, name="articles_info"),
                  path("reviews/", views.reviews, name="reviews"),
                  path("reviews/search", views.reviews_search, name="reviews_search"),
                  path("reviews/<str:pk>", views.reviews_info, name="reviews_info"),
                  path("species/", views.species, name="species"),
                  path("species/search", views.species_search, name="species_search"),
                  path("about/", views.about, name="about"),
                  path("doi/lookup", views.doi_lookup, name="doi_lookup"),
                  path("doi/import", views.doi_import, name="doi_import"),
                  # path("doi/<fullpath:doi>", views.doi_lookup, name="doi_lookup"),
              ])
               # + debug_toolbar_urls())
