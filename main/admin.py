from django.contrib import admin
from .models import Author, Species, Substrate, Topic, Method, Article, Review


# Author
@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
	list_display = ('name',)  # Fields to display in the list view
	search_fields = ('name',)  # Searchable fields
	ordering = ('name',)  # Order by the 'name' field


# Species
@admin.register(Species)
class SpeciesAdmin(admin.ModelAdmin):
	list_display = ('name',)
	search_fields = ('name', 'alternative_names')
	ordering = ('name',)


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
	fields = ('title', 'year', 'month', 'day', 'authors', 'journal', 'doi', 'species', 'substrate', 'topic', 'method', 'approved')  # Define the order of the fields   
	list_display = ('title', 'year', 'approved')
	search_fields = ('title', 'authors')
	ordering = ('-year', 'title')  # Order by 'year' (descending) and 'title'
	filter_horizontal = ('species', 'substrate', 'topic', 'method')  # Horizontal filter for many-to-many fields
	autocomplete_fields = ('authors', 'species', 'substrate', 'topic', 'method')

	# disable green "+" buttons to add new objects
	def get_form(self, request, obj=None, **kwargs):
		form = super(ArticleAdmin, self).get_form(request, obj, **kwargs)
		form.base_fields['topic'].widget.can_add_related = False
		form.base_fields['method'].widget.can_add_related = False
		return form


# Review
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
	fields = ('title', 'year', 'month', 'day', 'authors', 'journal', 'doi', 'topic', 'approved')
	list_display = ('title', 'year', 'approved')
	search_fields = ('title', 'authors')
	ordering = ('-year', 'title')
	filter_horizontal = ('topic',)
	autocomplete_fields = ('authors', 'topic')

	# disable green "+" buttons to add new objects
	def get_form(self, request, obj=None, **kwargs):
		form = super(ReviewAdmin, self).get_form(request, obj, **kwargs)
		form.base_fields['topic'].widget.can_add_related = False
		return form

		

