from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, F
from django.http import HttpResponseNotFound, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_POST

from fungalmaterials.doi import get_work_by_doi, import_new_article_by_doi
from fungalmaterials.forms import DOIImportForm, DOILookupForm
from fungalmaterials.models import Article, Review, MaterialProperty, ArticleAuthorship, ReviewAuthorship


############ ARTICLES ###########

def articles(request):
	context = {}
	return render(request, "fungalmaterials/articles.html", context)


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
		first_author_authorship = ArticleAuthorship.objects.filter(article=article, sequence='first').values_list('author__name', flat=True).first()
		# If no 'first' author exists, fall back to the first author added
		if not first_author_authorship:
			first_author_authorship = ArticleAuthorship.objects.filter(article=article).values_list('author__name', flat=True).first()
		payload.append({
			"title": article.title,
			"authors": first_author_authorship,
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
	# Get the article instance by the primary key (pk)
	article = get_object_or_404(Article, pk=pk)

	# Separate the author with sequence 'first'
	first_author_authorship = ArticleAuthorship.objects.filter(article=article, sequence='first').first()

	# If there is a first author, get the Author instance
	first_author = first_author_authorship.author if first_author_authorship else None

	# Get all other authors (those who are not 'first') and keep the original order
	other_authors_authorships = ArticleAuthorship.objects.filter(article=article).exclude(sequence='first')
	other_authors = [authorship.author for authorship in other_authors_authorships]

	# For species & substrate list
	sorted_species = article.species.all().order_by('name')
	sorted_substrate = article.substrate.all().order_by('name')

	# Query the MaterialProperty model for the specified article, ordered by species name
	material_properties = MaterialProperty.objects.filter(article=article).order_by('species__name')

	# Organize the data by species, treatment, and substrate
	data = {}
	unique_material_properties = {}

	for mp in material_properties:
		species = mp.species.name
		treatment = mp.treatment
		substrate = mp.substrate.name
		property_name = mp.material_property.name
		value = mp.value
		unit = mp.unit.symbol

		# Keep track of the unique material properties with units for column headers
		unique_material_properties[property_name] = unit

		# Ensure that species, treatment, and substrate exist in the dictionary
		if species not in data:
			data[species] = {}

		if treatment not in data[species]:
			data[species][treatment] = {}

		if substrate not in data[species][treatment]:
			data[species][treatment][substrate] = {}

		# Add the material property value to the correct species-treatment-substrate entry
		data[species][treatment][substrate][property_name] = value

	# Sort material properties for column headers
	sorted_material_properties = sorted(unique_material_properties.items())

	# Pass the data and sorted material properties to the template
	context = {
		'article': article,
		'first_author': first_author,
		'other_authors': other_authors,
		'data': data,
		'sorted_species': sorted_species,
		'sorted_substrate': sorted_substrate,
		'sorted_material_properties': sorted_material_properties,
	}

	return render(request, 'fungalmaterials/articles_info.html', context)


############ REVIEWS ###########

def reviews(request):
	context = {}
	return render(request, "fungalmaterials/reviews.html", context)


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
		first_author_authorship = ReviewAuthorship.objects.filter(review=review, sequence='first').values_list('author__name', flat=True).first()
		# If no 'first' author exists, fall back to the first author added
		if not first_author_authorship:
			first_author_authorship = ReviewAuthorship.objects.filter(review=review).values_list('author__name', flat=True).first()
		payload.append({
			"title": review.title,
			"authors": first_author_authorship,
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
	# Separate the author with sequence 'first'
	first_author_authorship = ReviewAuthorship.objects.filter(review=review, sequence='first').first()

	# If there is a first author, get the Author instance
	first_author = first_author_authorship.author if first_author_authorship else None

	# Get all other authors (those who are not 'first') and keep the original order
	other_authors_authorships = ReviewAuthorship.objects.filter(review=review).exclude(sequence='first')
	other_authors = [authorship.author for authorship in other_authors_authorships]

	context = {
		'review': review,
		'first_author': first_author,
		'other_authors': other_authors,
	}

	if review.approved:
		return render(request, "fungalmaterials/reviews_info.html", context)
	else:
		return HttpResponseNotFound("<h1>Page not found</h1>")


############ SPECIES ###########

def species(request):
	context = {}
	return render(request, "fungalmaterials/species.html", context)


def species_search(request):
	# Query the MaterialProperty model for all data
	material_properties = MaterialProperty.objects.select_related('species', 'substrate', 'material_property', 'article')

	# Prepare data to send as JSON
	data = []
	property_names = set()  # To track unique material properties
	property_values = {}  # To store values for each unique species, treatment, and substrate

	for mp in material_properties:
		species = mp.species.name
		treatment = mp.treatment or "-"
		substrate = mp.substrate.name
		property_name = mp.material_property.name
		value = mp.value
		unit = mp.unit.symbol
		topic = mp.article.topic
		method = mp.article.method
		first_author = mp.article.authors.values_list('name', flat=True).first()
		article_reference = f"{first_author} ({mp.article.year})"

		# Track unique material property names
		property_names.add(property_name)

		# Create a unique key for each combination of species, treatment, and substrate
		key = (species, treatment, substrate)
		if key not in property_values:
			property_values[key] = {
				'species': species,
				'treatment': treatment,
				'substrate': substrate,
				'topic': list(topic.values_list('name', flat=True)),
				'method': list(method.values_list('name', flat=True)),
				'article': article_reference,
				# Initialize all properties with a placeholder
				**{prop: '-' for prop in property_names}
			}

		# Update the value for the material property
		property_values[key][property_name] = f"{value} {unit}"

	# Convert dictionary to list
	data = list(property_values.values())

	# Return the data as JSON for DataTable consumption
	return JsonResponse({
		'data': data,
		'property_names': list(property_names)  # Include unique material property names
	})


############ DOI Lookup ###########
# The correct text to compare against
CORRECT_TEXT = "correct"

# This view presents a form to ask for a DOI. If the entry can be resolved to a valid article, it will show that.
# If it could not be resolved, it will show an error.
@login_required
def doi_lookup(request):
	# If this was a POST, someone has used the submit button, check the input
	if request.method == 'POST':
		form = DOILookupForm(request.POST)
		if form.is_valid():
			# We know that the value is not empty, so we can take this DOI and ask the API about it
			possible_work = get_work_by_doi(form.cleaned_data['doi'])
			if possible_work:
				# If the API finds something, present this to the user
				import_form = DOIImportForm(initial={'doi': form.cleaned_data['doi']})
				# import_form.fields['doi']
#				import_form.doi = form.cleaned_data['doi']
				return render(request, 'fungalmaterials/doi_import_preview.html', {'form': import_form, 'doi_preview': possible_work })
			else:
				# If the API finds nothing, let the user know this DOI didn't get us anything.
				form.add_error('doi', 'The DOI you entered is incorrect.')
	else:
		form = DOILookupForm()

	return render(request, 'fungalmaterials/doi_input_form.html', {'form': form})

# View for handling success
@login_required
@require_POST
def doi_import(request):

	form = DOIImportForm(request.POST)

	if form.is_valid():
		import_status = import_new_article_by_doi(form.cleaned_data['doi'])
		if import_status:
			# TODO: Fix placeholder data
			return render(request, 'fungalmaterials/doi_import_done.html',
						  {'article_id': "2345asdf2345", 'doi_id': form.cleaned_data['doi']})
		else:
			form.add_error('doi', f"The DOI {form.cleaned_data['doi']} could not be imported.")

	else:
		form.add_error('doi', 'The DOI you entered is incorrect.')

	return render(request, 'fungalmaterials/doi_import_preview.html', {'form': form})


# @login_required
# @require_GET
# def doi_lookup(request, doi):
# 	# Check if the doi string is provided (this will always be true due to URL config)
# 	if not doi:
# 		return JsonResponse(
# 			{'error': 'DOI not found.'},
# 			status=404
# 		)
#
# 	# Check if the doi string is shorter than 3 characters
# 	if len(doi) < 3:
# 		return JsonResponse(
# 			{'error': 'DOI is invalid. Must be at least 3 characters long.'},
# 			status=400  # 400 Bad Request for invalid input
# 		)
#
# 	# If all validations pass,
# 	cr = Crossref(mailto="j.g.vandenbrandhof@uu.nl")
# 	print(f"Looking for {doi}")
# 	works_found = cr.works(ids=[doi])
#
# 	# #then return a success response
# 	return JsonResponse(
# 		{'message': f'DOI "{doi}" is valid and accepted.', 'works': works_found},
# 		status=200
# 	)

############ ABOUT ###########

def about(request):
	context = {}
	return render(request, "fungalmaterials/about.html", context)

