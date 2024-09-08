from asyncio.log import logger
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.db.models import Max, Min, Count, Q, F, Value, IntegerField, Subquery, OuterRef
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Species, Substrate, Topic, Method, Article, Review, Property, Unit, MaterialProperty


############ ARTICLES ###########

def articles(request):
	context = {}
	return render(request, "main/articles.html", context)


def articles_search(request):
	# Get the start position and search value
	start_position = int(request.GET.get('start', 0))
	search_query = request.GET.get('search[value]', '')

	# Default sorting parameters
	record_order_sorting = "asc"
	record_column_id = 0

	field_to_column = {
		"0": "title",
		# "1": "authors", # off because manytomany field
		"2": "year",
		# "3": "topic", # off because manytomany field
		# "4": "method", # off because manytomany field
	}

	# Process sorting parameters
	order_column_index = request.GET.get('order[0][column]', '0')
	order_direction = request.GET.get('order[0][dir]', 'asc')

	# Update the field to column mapping if necessary
	if order_column_index in field_to_column:
		order_field = field_to_column[order_column_index]
	else:
		order_field = "title"

	# Determine sorting direction
	if order_direction == 'desc':
		order_field = F(order_field).desc(nulls_last=True)
	else:
		order_field = F(order_field).asc(nulls_last=True)

	# Filter and sort articles
	article_query = Article.objects.filter(approved=True)
	
	if search_query:
		article_query = article_query.filter(
			Q(title__icontains=search_query) |
			Q(authors__name__icontains=search_query) |
			Q(year__icontains=search_query) |
			Q(topic__name__icontains=search_query) |
			Q(method__name__icontains=search_query)
		).distinct()

	# Apply ordering
	article_query = article_query.order_by(order_field)

	# Pagination
	paginator = Paginator(article_query, 125)
	page_number = (start_position // 125) + 1

	try:
		articles_page = paginator.page(page_number)
	except PageNotAnInteger:
		articles_page = paginator.page(1)
	except EmptyPage:
		articles_page = paginator.page(paginator.num_pages)

	# Prepare the data payload
	payload = []
	for article in articles_page:
		first_author = article.authors.values_list('name', flat=True).first()
		payload.append({
			"title": article.title,
			"authors": first_author,
			"year": article.year,
			"topic": list(article.topic.values_list('name', flat=True)),
			"method": list(article.method.values_list('name', flat=True)),
			"pk": article.pk,
		})

	# Prepare response data
	response_data = {
		"recordsTotal": paginator.count,
		"recordsFiltered": article_query.count(),
		"data": payload,
	}

	return JsonResponse(response_data)


def articles_info(request, pk):
	article = Article.objects.get(id=pk)
	sorted_species = article.species.all().order_by('name')
	material_property = MaterialProperty.objects.filter(article=article).values_list('species', flat=True).distinct()


	# Get distinct treatments for the article
	distinct_treatments = MaterialProperty.objects.filter(article=article).values_list('treatment', flat=True).distinct()

	# Get distinct material property names for the article (e.g., "Density", "Elongation")
	distinct_properties = MaterialProperty.objects.filter(article=article).values_list('material_property__name', flat=True).distinct()

	context = {
		'article': article,
		'sorted_species': sorted_species,
		'material_property': material_property,
		'distinct_treatments': distinct_treatments,
		'distinct_properties': distinct_properties,
	}

	if article.approved:
		return render(request, "main/articles_info.html", context)
	else:
		return HttpResponseNotFound("<h1>Page not found</h1>")


############ REVIEWS ###########

def reviews(request):
	context = {}
	return render(request, "main/reviews.html", context)


def reviews_search(request):
	# Get the start position and search value
	start_position = int(request.GET.get('start', 0))
	search_query = request.GET.get('search[value]', '')

	# Default sorting parameters
	record_order_sorting = "asc"
	record_column_id = 0

	field_to_column = {
		"0": "title",
		# "1": "authors", # off because manytomany field
		"2": "year",
		# "3": "topic", # off because manytomany field
	}

	# Process sorting parameters
	order_column_index = request.GET.get('order[0][column]', '0')
	order_direction = request.GET.get('order[0][dir]', 'asc')

	# Update the field to column mapping if necessary
	if order_column_index in field_to_column:
		order_field = field_to_column[order_column_index]
	else:
		order_field = "title"

	# Determine sorting direction
	if order_direction == 'desc':
		order_field = F(order_field).desc(nulls_last=True)
	else:
		order_field = F(order_field).asc(nulls_last=True)

	# Filter and sort reviews
	review_query = Review.objects.filter(approved=True)
	
	if search_query:
		review_query = review_query.filter(
			Q(title__icontains=search_query) |
			Q(authors__name__icontains=search_query) |
			Q(year__icontains=search_query) |
			Q(topic__name__icontains=search_query)
		).distinct()

	# Apply ordering
	review_query = review_query.order_by(order_field)

	# Pagination
	paginator = Paginator(review_query, 125)
	page_number = (start_position // 125) + 1

	try:
		reviews_page = paginator.page(page_number)
	except PageNotAnInteger:
		reviews_page = paginator.page(1)
	except EmptyPage:
		reviews_page = paginator.page(paginator.num_pages)

	# Prepare the data payload
	payload = []
	for review in reviews_page:
		first_author = review.authors.values_list('name', flat=True).first()
		payload.append({
			"title": review.title,
			"authors": first_author,
			"year": review.year,
			"topic": list(review.topic.values_list('name', flat=True)),
			"pk": review.pk,
		})

	# Prepare response data
	response_data = {
		"recordsTotal": paginator.count,
		"recordsFiltered": review_query.count(),
		"data": payload,
	}

	return JsonResponse(response_data)


def reviews_info(request, pk):
	review = Review.objects.get(id=pk)

	context = {
		'review': review,
	}

	if review.approved:
		return render(request, "main/reviews_info.html", context)
	else:
		return HttpResponseNotFound("<h1>Page not found</h1>")


############ SPECIES ###########

def species(request):
	context = {}
	return render(request, "main/species.html", context)


def species_search(request):
# Get the start position and search value
	start_position = int(request.GET.get('start', 0))
	search_query = request.GET.get('search[value]', '')

	# Default sorting parameters
	record_order_sorting = "asc"
	record_column_id = 0

	field_to_column = {
		"0": "species",
		"1": "property",
		#"2": "topic", # off because manytomany field
		#"3": "method", # off because manytomany field
		"4": "article"
	}

	# Process sorting parameters
	order_column_index = request.GET.get('order[0][column]', '0')
	order_direction = request.GET.get('order[0][dir]', 'asc')

	# Update the field to column mapping if necessary
	if order_column_index in field_to_column:
		order_field = field_to_column[order_column_index]
	else:
		order_field = "species"

	# Determine sorting direction
	if order_direction == 'desc':
		order_field = F(order_field).desc(nulls_last=True)
	else:
		order_field = F(order_field).asc(nulls_last=True)

	# Prepare the base query
	material_property_query = MaterialProperty.objects.select_related('article').prefetch_related('species', 'article__topic', 'article__method')

	# Filtering based on search query
	if search_query:
		material_property_query = material_property_query.filter(
			Q(species__name__icontains=search_query) |
			Q(treatment__icontains=search_query) |
			Q(material_property__name__icontains=search_query) |
			Q(article__title__icontains=search_query) |
			Q(article__topic__name__icontains=search_query) |
			Q(article__method__name__icontains=search_query)
		).distinct()

	# Apply ordering
	# Note: Sorting by fields that are not directly part of the MaterialProperty model needs special handling
	# For simplicity, we will sort by species name as a default approach
	if order_field == "species":
		material_property_query = material_property_query.order_by('species__name')
	elif order_field == "property":
		material_property_query = material_property_query.order_by('material_property__name')
	elif order_field == "topic":
		material_property_query = material_property_query.order_by('article__topic__name')
	elif order_field == "method":
		material_property_query = material_property_query.order_by('article__method__name')
	elif order_field == "article":
		material_property_query = material_property_query.order_by('article__title')

	# Pagination
	paginator = Paginator(material_property_query, 125)
	page_number = (start_position // 125) + 1

	try:
		properties_page = paginator.page(page_number)
	except PageNotAnInteger:
		properties_page = paginator.page(1)
	except EmptyPage:
		properties_page = paginator.page(paginator.num_pages)

	# Prepare the data payload
	payload = []
	for material_property in properties_page:
		species_name = material_property.species.name
		treatment = material_property.treatment
		property_name = material_property.material_property.name
		first_author = material_property.article.authors.first()
		first_author_name = first_author.name if first_author else "Unknown"
		year = material_property.article.year if material_property.article.year else "Unknown"
		article_info = f"{first_author_name} ({year})"

		payload.append({
			"species": species_name,
			"treatment": treatment,
			"property": property_name,
			"topic": list(material_property.article.topic.values_list('name', flat=True)),
			"method": list(material_property.article.method.values_list('name', flat=True)),
			"article": article_info,
			"pk": material_property.article.pk,
		})

	# Prepare response data
	response_data = {
		"recordsTotal": paginator.count,
		"recordsFiltered": material_property_query.count(),
		"data": payload,
	}

	return JsonResponse(response_data)
	

############ ABOUT ###########

def about(request):
	context = {}
	return render(request, "main/about.html", context)

