from asyncio.log import logger
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.db.models import Max, Min, Count, Q, F, Value, IntegerField, Subquery, OuterRef
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Species, Substrate, Topic, Method, Article, Review


############ ARTICLES ###########

def articles(request):
	query = request.GET.get('q')
	object_list = Article.objects.all().order_by('title')

	context = {
		'object_list': object_list,
		'query': query or '',
		}

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

	context = {
		'article': article,
		'sorted_species': sorted_species,
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


############ ABOUT ###########

def about(request):
	context = {}
	return render(request, "main/about.html", context)

