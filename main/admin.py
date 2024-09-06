from django.contrib import admin
from .models import Species, Substrate, Topic, Method, Article, Review

# Species
@admin.register(Species)
class SpeciesAdmin(admin.ModelAdmin):
    list_display = ('name',)  # Fields to display in the list view
    search_fields = ('name', 'alternative_names')  # Searchable fields
    ordering = ('name',)  # Order by the 'name' field


# Substrate
@admin.register(Substrate)
class SubstrateAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    ordering = ('name',)


# Topic
@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    ordering = ('name',)


# Growth method
@admin.register(Method)
class MethodAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    ordering = ('name',)


# Article
@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'year', 'approved')
    list_filter = ('approved', 'year', 'species', 'substrate', 'topic', 'method')
    search_fields = ('title', 'authors')
    ordering = ('-year', 'title')  # Order by 'year' (descending) and 'title'
    filter_horizontal = ('species', 'substrate', 'topic', 'method')  # Horizontal filter for many-to-many fields
    autocomplete_fields = ('species', 'substrate')


# Review
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
	list_display = ('title', 'year', 'approved')
	search_fields = ('title', 'authors')
	ordering = ('-year', 'title')
