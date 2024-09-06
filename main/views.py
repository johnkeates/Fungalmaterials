import json
from asyncio.log import logger
from django.shortcuts import render
from django.http import HttpResponse
from django.db.models import Max, Min, Count, Q, F, Value, IntegerField, Subquery, OuterRef
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Species, Substrate, Topic, Method, Article, Review


def articles(request):
	query = request.GET.get('q')
	object_list = Article.objects.all().order_by('title')

	context = {
		'object_list': object_list,
		'query': query or '',
		}

	return render(request, "main/articles.html", context)


def articles_search(request):
	# Get the start position as requested by DataTables
	startPositionString = request.GET.get('start')
	# Get the search value (if any)
	searchQuery = request.GET.get('search[value]')

	try:
		startPosition = abs(int(startPositionString))
	except TypeError:
		logger.critical("startPosition not an integer, setting to 0")
		startPosition = 0
	except ValueError:
		logger.critical("startPosition not usable, setting to 0")
		startPosition = 0

	record_order_sorting = "asc"

	record_column_id = 0

	field_to_column = {
		"0": "title",
		"1": "authors",
		"2": "year",
		"3": "topic",
		"4": "method",
	}

	for url_parameter in request.GET.dict():
		if url_parameter.startswith("order"):
			if "dir" in url_parameter:
				record_order_sorting = "desc" if request.GET.get(url_parameter) == "desc" else "asc"
			if "column" in url_parameter:
				record_column_id = request.GET.get(url_parameter)
		if url_parameter.startswith("columns") and "[data]" in url_parameter:
			parts = url_parameter.split("]")[0].split("[")
			if len(parts) == 2:
				col_id = parts[1]
				field_value = request.GET.get(url_parameter)
				field_parts = field_value.split(".")
				if len(field_parts) == 2:
					field_to_column[col_id] = field_parts[1]

	if record_column_id in field_to_column:
		record_order_field = field_to_column[record_column_id]
	else:
		record_order_field = "title"

	# Order by the specified field, with null values last
	if record_order_sorting == "desc":
		record_order_field = F(record_order_field).desc(nulls_last=True)
	else:
		record_order_field = F(record_order_field).asc(nulls_last=True)

	unfilteredCount = Article.objects.filter(approved=True).all().count()
	filteredCount = unfilteredCount

	if searchQuery:
		object_list = Article.objects.filter(approved=True).filter(Q(title__icontains=searchQuery) 
			| Q(authors__icontains=searchQuery) | Q(year__icontains=searchQuery))
		filteredCount = object_list.count()
	else:
		object_list = Article.objects.filter(approved=True)

	paginator = Paginator(object_list, 125)

	try:
		object_list = paginator.page(1 + (startPosition / 125))
	except PageNotAnInteger:
		object_list = paginator.page(1)
	except EmptyPage:
		object_list = paginator.page(paginator.num_pages)

	payload = []
	for article in object_list:
		if article.approved:  # check if the article is approved
			# Split the authors string by commas and take the first author
			first_author = article.authors.split(',')[0].strip() if article.authors else ''

			payload.append({
				"title": article.title,
				"authors": first_author,
				"year": article.year,
				# Serialize ManyToMany fields to lists of names
				"topic": list(article.topic.values_list('name', flat=True)),
				"method": list(article.method.values_list('name', flat=True)),
				"pk": article.pk,
			})

	return HttpResponse('{"recordsTotal": ' + str(unfilteredCount) + ', "recordsFiltered": ' + str(
		filteredCount) + ',"data": ' + json.dumps(payload) + "}",
		content_type='application/json')


def reviews(request):
	context = {}
	return render(request, "main/reviews.html", context)


def about(request):
	context = {}
	return render(request, "main/about.html", context)

