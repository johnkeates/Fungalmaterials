from django.contrib import admin
from django.utils.safestring import mark_safe

from fungalmaterials.models import Author, Species, Substrate, Topic, Method, Article, Review, Property, Unit, Material, ArticleAuthorship, ReviewAuthorship


# Author
@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
	list_display = ('name', 'family')  # Fields to display in the list view
	search_fields = ('name', 'family')  # Searchable fields
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


# Article-Author relationship
class ArticleAuthorshipInline(admin.TabularInline):
	model = ArticleAuthorship
	extra = 2

# Custom widget for the Article form to enable the 'prefill this article' feature
from django import forms
from django.contrib import admin


class ArticleDoiImportWidget(forms.CheckboxInput):
	template_name = 'admin/widgets/article_doi_import_widget.html'

class ArticleAdminForm(forms.ModelForm):
	class Meta:
		model = Article
		fields = '__all__'
		widgets = {
			'doi_import': ArticleDoiImportWidget(),
		}

# End Custom Widget



# Article
@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
	inlines = [ArticleAuthorshipInline]
	form = ArticleAdminForm
	fields = ('title', 'year', 'month', 'day', 'journal', 'doi', 'species', 'substrate', 'topic', 'method', 'abstract', 'approved')  # Define the order of the fields   
	list_display = ('title', 'year', 'approved')
	search_fields = ('title',)
	ordering = ('-year', 'title')  # Order by 'year' (descending) and 'title'
	filter_horizontal = ('species', 'substrate', 'topic', 'method')  # Horizontal filter for many-to-many fields
	autocomplete_fields = ('species', 'substrate', 'topic', 'method')

	# disable green "+" buttons to add new objects
	def get_form(self, request, obj=None, **kwargs):
		form = super(ArticleAdmin, self).get_form(request, obj, **kwargs)
		form.base_fields['title'].widget.attrs['style'] = 'width: 40em;' # Change width of specific field
		form.base_fields['topic'].widget.can_add_related = False
		form.base_fields['method'].widget.can_add_related = False
		# form.base_fields['doi'].help_text = mark_safe(
		# 	"<a href='#' id='doilookup'>Check DOI for autocomplete information</a>"
		# 	"<script src='/static/doi-lookup.js'></script>"
		# )
		return form


# Review-Author relationship
class ReviewAuthorshipInline(admin.TabularInline):
	model = ReviewAuthorship
	extra = 2


# Review
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
	inlines = [ReviewAuthorshipInline]
	fields = ('doi', 'title', 'year', 'month', 'day', 'journal', 'topic', 'abstract', 'approved')
	list_display = ('title', 'year', 'approved')
	search_fields = ('title',)
	ordering = ('-year', 'title')
	filter_horizontal = ('topic',)
	autocomplete_fields = ('topic',)

	# disable green "+" buttons to add new objects
	def get_form(self, request, obj=None, **kwargs):
		form = super(ReviewAdmin, self).get_form(request, obj, **kwargs)
		form.base_fields['topic'].widget.can_add_related = False
		return form


# Property
@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
	list_display = ('name',)
	search_fields = ('name',)


# Unit
@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
	list_display = ('symbol', 'name')
	search_fields = ('symbol', 'name')


# Material
@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
	list_display = ('get_first_author_and_year', 'species', 'substrate', 'treatment', 'material_property', 'value', 'unit')
	search_fields = ('article__name', 'species__name', 'substrate__name', 'material_property__name')
	autocomplete_fields = ('article', 'species', 'substrate')

	# Custom method to get the first author and year of the article
	def get_first_author_and_year(self, obj):
		authors = obj.article.authors.all()  # Get all authors related to the article
		if authors.exists():
			first_author = authors[0].name  # Get the first author's name
		else:
			first_author = "No author"  # Fallback if no authors are present
		
		# Get the year from the related article
		year = obj.article.year if obj.article.year else "Unknown year"
		
		# Return the format: "Author Name (Year)"
		return f"{first_author} ({year})"

	# Rename the column in the admin panel
	get_first_author_and_year.short_description = 'First Author (Year)'
		
