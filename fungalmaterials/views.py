import json
import operator
from collections import defaultdict
from functools import reduce

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, F, Value, Count
from django.db.models.functions import Coalesce
from django.forms import model_to_dict
from django.http import HttpResponseNotFound, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from bs4 import BeautifulSoup
import plotly.graph_objects as go
from habanero.filterhandler import switch
from django.core import serializers
from django.utils.safestring import mark_safe

from fungalmaterials.functions import author_separation
from fungalmaterials.combinations import generate_sankey
from fungalmaterials.doi import get_work_by_doi, import_new_article_by_doi, import_new_review_by_doi
from fungalmaterials.forms import DOIImportForm, DOISearchForm
from fungalmaterials.models import Article, Review, Material, ArticleAuthorship, ReviewAuthorship, Species, Topic, \
    Method


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
        "2": "year",  # This will now include year, month, and day sorting
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
    sort_asc = order_direction == 'asc'

    # Filter and sort articles
    article_query = Article.objects.filter(approved=True)

    if search_query:
        article_query = article_query.filter(
            Q(title__icontains=search_query) |
            Q(authors__family__icontains=search_query) |
            Q(year__icontains=search_query) |
            Q(material__topic__name__icontains=search_query) |
            Q(material__method__name__icontains=search_query)
        ).distinct()

    # Apply ordering
    if order_field == "year":
        # Sort by year, then by month (default to 0 if None), and then by day (default to 0 if None)
        if sort_asc:
            article_query = article_query.order_by(
                F('year').asc(nulls_last=True),
                Coalesce('month', Value(0)).asc(),
                Coalesce('day', Value(0)).asc()
            )
        else:
            article_query = article_query.order_by(
                F('year').desc(nulls_last=True),
                Coalesce('month', Value(0)).desc(),
                Coalesce('day', Value(0)).desc()
            )
    else:
        if sort_asc:
            article_query = article_query.order_by(F(order_field).asc(nulls_last=True))
        else:
            article_query = article_query.order_by(F(order_field).desc(nulls_last=True))

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
        first_author_authorship = ArticleAuthorship.objects.filter(article=article, sequence='first').values_list(
            'author__family', flat=True).first()
        # If no 'first' author exists, fall back to the first author added
        if not first_author_authorship:
            first_author_authorship = ArticleAuthorship.objects.filter(article=article).values_list('author__family',
                                                                                                    flat=True).first()

        # Get all topics and methods from the associated materials, excluding null values
        material_topics = Material.objects.filter(article=article).exclude(
            topic__name__isnull=True
        ).values_list('topic__name', flat=True)

        material_methods = Material.objects.filter(article=article).exclude(
            method__name__isnull=True
        ).values_list('method__name', flat=True)

        # Ensure uniqueness of topics and methods
        unique_topics = set(material_topics)
        unique_methods = set(material_methods)

        # Append to payload
        payload.append({
            "title": article.title,
            "authors": first_author_authorship,
            "year": article.year,
            "topic": list(unique_topics),
            "method": list(unique_methods),
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
    article.title = mark_safe(article.title)
    article.abstract = mark_safe(article.abstract)

    # Get all article authors
    authors_list = article.authors.all()

    # Apply function to separate authors with "," or "&"
    authors_list = author_separation(authors_list)

    # For species & substrate list
    sorted_species = []
    sorted_substrate = []

    for material in article.material_set.all():
        for species in material.species.all():
            sorted_species.append(species)

        for substrate in material.substrates.all():
            sorted_substrate.append(substrate)

    # Order sorted_species from A-Z based on name
    sorted_species.sort(key=lambda species: species.name)

    # Material properties list, ordered by species name
    material_properties = []

    # For method and topics
    material_topics = Material.objects.filter(article=article).exclude(topic__name__isnull=True).values_list('topic__name', flat=True).distinct()
    material_methods = Material.objects.filter(article=article).exclude(method__name__isnull=True).values_list('method__name', flat=True).distinct()

    context = {
        'article': article,
        'authors_list': authors_list,
        'sorted_species': sorted_species,
        'sorted_substrate': sorted_substrate,
        'material_properties': material_properties,
        'material_topics': material_topics,
        'material_methods': material_methods,
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
            Q(authors__family__icontains=search_query) |
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
        first_author_authorship = ReviewAuthorship.objects.filter(review=review, sequence='first').values_list(
            'author__family', flat=True).first()
        # If no 'first' author exists, fall back to the first author added
        if not first_author_authorship:
            first_author_authorship = ReviewAuthorship.objects.filter(review=review).values_list('author__family',
                                                                                                 flat=True).first()
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
    review.title = mark_safe(review.title)
    review.abstract = mark_safe(review.abstract)

    # Get all article authors
    authors_list = review.authors.all()

    # Apply function to separate authors with "," or "&"
    authors_list = author_separation(authors_list)

    context = {
        'review': review,
        'authors_list': authors_list,
    }

    if review.approved:
        return render(request, "fungalmaterials/reviews_info.html", context)
    else:
        return HttpResponseNotFound("<h1>Page not found</h1>")


############ SPECIES ###########

def species(request):
    context = {}
    return render(request, "fungalmaterials/species.html", context)


@csrf_exempt
def species_search(request):
    # We work with POST data here to receive SearchPane, Column and Search inputs:
    if request.method == "POST":
        # Is the body non-empty (i.e. has JSON)
        if request.body:
            try:
                # Attempt to decode the JSON body
                json_data = json.loads(request.body)
            except json.JSONDecodeError:
                # Return an error response if decoding fails
                return JsonResponse({"error": "Invalid JSON data"}, status=400)

            # Prepare a map to hold the unique count of Phylum, Species etc. for SearchPanes
            # Keys we want to track in the dictionaries
            list_of_search_pane_names = ["species", "phylum", "topic", "method"]

            # Create a defaultdict where each key's counter is also a defaultdict(int)
            list_of_search_pane_name_filters = {pane: [] for pane in list_of_search_pane_names}

            # Check if we had a search query
            if "search" in json_data:
                if json_data["search"]:
                    if json_data["search"]["value"]:
                        # We have a live search query
                        print("User searched for:", json_data["search"])
                        # Topic Name must match
                        # Method
                        # Species
                        # Phylum

            # Start decoding the searchPanes, if any
            if "searchPanes" in json_data:
                # Check each entry in the searchpane dict
                for search_pane_name in json_data["searchPanes"]:
                    # If the dict is not empty, decode the contents
                    if json_data["searchPanes"][search_pane_name]:
                        # But only if we already know this search pane
                        if search_pane_name in list_of_search_pane_names:
                            # Add each selected option to the list of filters
                            for species_text in json_data["searchPanes"][search_pane_name]:
                                list_of_search_pane_name_filters[search_pane_name].append(json_data["searchPanes"][search_pane_name][species_text])
                        else:
                            print("Searchpane not in known list:", search_pane_name)

            print("Requested filters:", list_of_search_pane_name_filters)

            # We get all materials. A material might have a lot of details,
            # but it has one requirement: connecting an article to a species.
            # This means we only want Material entries that exist at least once in the Species relationship,
            # or, in other words, Materials that have at least 1 species listed in their Model.
            material_query = Material.objects.filter(species__isnull=False)


            # If we have to filter things based on the SearchPanes, we list those filters here to be appended later
            material_filter_clauses = []

            # The following clauses will be used to filter records when we discover the first pass returned too much
            # related data, like a material that has two species but we only want to show the first one.
            post_fetch_filter_clauses = []

            # Check if we need to filter on species:
            if len(list_of_search_pane_name_filters['species']) > 0:
                # The filter below will remove any Material that does not have the listed Species as a component,
                # but if the Material is made using multiple Species, the entire material will still be fetched.
                material_filter_clauses.append(Q(species__name__in=list_of_search_pane_name_filters['species']))

                # Make sure to post-filter the discovered Materials when rendering the final return data to only include
                # the individual rows we want.
                post_fetch_filter_clauses.append(Q(name__in=list_of_search_pane_name_filters['species']))

            # Check if we need to filter on species:
            if len(list_of_search_pane_name_filters['topic']) > 0:
                # We have topics to filter!
                # print("Filtering topics", list_of_search_pane_name_filters['topic'])
                # material_query = material_query.filter(article__topic__name__in=list_of_search_pane_name_filters['topic'])

                material_filter_clauses.append(Q(topic__name__in=list_of_search_pane_name_filters['topic']))
                # print(species_query.values())
                # print("topics Query SQL:", species_query.query)

            # Check if we need to filter on phylum:
            if len(list_of_search_pane_name_filters['phylum']) > 0:
                # We have topics to filter!
                # print("Filtering topics", list_of_search_pane_name_filters['topic'])
                #                material_query = material_query.filter(article__topic__name__in=list_of_search_pane_name_filters['topic'])

                print(Species.objects.filter(phylum__in=list_of_search_pane_name_filters['phylum']))

                material_filter_clauses.append(Q(species__phylum__in=list_of_search_pane_name_filters['phylum']))

                post_fetch_filter_clauses.append(Q(phylum__in=list_of_search_pane_name_filters['phylum']))

            # Check if we need to filter on phylum:
            if len(list_of_search_pane_name_filters['method']) > 0:
                # We have topics to filter!
                # print("Filtering topics", list_of_search_pane_name_filters['topic'])
                #                material_query = material_query.filter(article__topic__name__in=list_of_search_pane_name_filters['topic'])

                #print(Species.objects.filter(method__in=list_of_search_pane_name_filters['method']))

                material_filter_clauses.append(Q(method__name__in=list_of_search_pane_name_filters['method']))

                # post_fetch_filter_clauses.append(Q(method__in=list_of_search_pane_name_filters['method']))

                # print(species_query.values())
                # print("topics Query SQL:", species_query.query)

            # Prepare an empty list to hold data for JSON response
            payload_data = []

            # Create a defaultdict where each key's counter is also a defaultdict(int)
            column_name_unique_values = {key: defaultdict(int) for key in list_of_search_pane_names}


            # Create a defaultdict just like the one above, but with complete database counts
            column_name_total_values = {key: defaultdict(int) for key in list_of_search_pane_names}

            # Generalized function to count unique values for a model field
            def count_unique_values(model, field_name, column_key):
                counts = model.objects.values(field_name).annotate(count=Count(field_name))
                for entry in counts:
                    unique_value = entry[field_name]
                    count = entry['count']
                    column_name_total_values[column_key][unique_value] = count

            # Call the function for each model and field
            count_unique_values(Topic, 'name', 'topic')
            count_unique_values(Method, 'name', 'method')
            count_unique_values(Species, 'name', 'species')
            count_unique_values(Species, 'phylum', 'phylum')

            print(column_name_total_values)

            # If any SearchPanes were used, there will be filter clauses that need to be applied to the query:
            if material_filter_clauses:
                material_query = material_query.filter(reduce(operator.and_, material_filter_clauses))

            print(material_query.query)

            # From the returned materials we want to extract a list of species and their material properties
            for material in material_query:
                # Get all the species embedded in this material definition
                species_in_material = material.species.all()

                # If any SearchPanes were used, there will be filter clauses that need to be applied to the query:
                if post_fetch_filter_clauses:
                    species_in_material = species_in_material.filter(reduce(operator.and_, post_fetch_filter_clauses))

                #print(species_in_material.query)

                # For every found species, get the properties of the current material:
                # - mechanical/measured properties
                # - article properties (the one connected to this material)
                # - authors for the article
                # this is what is used to construct the final payload for the table.
                # Inside the Table we will need access to the underlying material for the reported species.
                # It is possible multiple materials have the same species, but they will be listed multiple times
                # for every unique combination of species<--->material<--->article.
                for embedded_species in species_in_material:

                    # Get the first author based on sequence
                    first_author_authorship = material.article.articleauthorship_set.filter(sequence='first').values_list('author__family', flat=True).first()

                    # If no 'first' author exists, fall back to the first author added
                    if not first_author_authorship:
                        first_author_authorship = material.article.articleauthorship_set.first().values_list(
                            'author__family', flat=True).first()

                    # We count the specifics of the current species so we can show the SearchPane match counters
                    # These two are always single matching
                    column_name_unique_values["species"][embedded_species.name] += 1
                    column_name_unique_values["phylum"][embedded_species.phylum] += 1

                    # These two are lists so can contain 0 to * options
                    for individual_topic in material.topic.all():
                        column_name_unique_values["topic"][individual_topic.name] += 1

                    for individual_method in material.method.all():
                        # print("Adding method: ", individual_method.name)
                        column_name_unique_values["method"][individual_method.name] += 1

                    # Append a dictionary of selected fields to payload_data for each material
                    payload_data.append({
                        "pk": f"{material.id}{embedded_species.id}",  # OK
                        "article_id": material.article.id,  # OK
                        "treatment": material.treatment,  # OK
                        "species": embedded_species.name,  # OK
                        "substrates": list(material.substrates.values()),  # OK
                        "method": list(material.method.values()),  # OK
                        "topic": [individual_topic.name for individual_topic in material.topic.all()],  # OK
                        "properties": [
                            {
                                "value": prop.value,  # Property value
                                "name": prop.name.name,  # Property name (from the related PropertyName model)
                                "unit": prop.unit.symbol  # Unit of the property (from the related Unit model)
                            }
                            # Loop over each property associated with the material
                            for prop in material.property_set.all()
                        ],
                        "phylum": embedded_species.phylum,
                        "first_author": first_author_authorship,
                        # Use the first author (either by sequence or fallback)
                        "article_reference": f"{first_author_authorship} ({material.article.year})"
                        # Reference with first author
                    })


            # The DataTable will always send us some information about the table state:
            # draw 1
            # columns [
            # 			{'data': 'species', 'name': '', 'searchable': True, 'orderable': True, 'search': {'value': '', 'regex': False, 'fixed': []}},
            # 			{'data': 'treatment', 'name': '', 'searchable': False, 'orderable': False, 'search': {'value': '', 'regex': False, 'fixed': []}},
            # 			{'data': 'topic', 'name': '', 'searchable': False, 'orderable': False, 'search': {'value': '', 'regex': False, 'fixed': []}},
            # 			{'data': 'method', 'name': '', 'searchable': False, 'orderable': False, 'search': {'value': '', 'regex': False, 'fixed': []}},
            # 			{'data': 'article_reference', 'name': '', 'searchable': False, 'orderable': False, 'search': {'value': '', 'regex': False, 'fixed': []}}
            #		]
            # order [{'column': 0, 'dir': 'asc', 'name': ''}]
            # start 0
            # length 125
            # search {'value': '', 'regex': False, 'fixed': []}
            # searchPanes {'species': {'0': 'Flammulina velutipes'}, 'treatment': {}, 'topic': {}, 'method': {}, 'article_reference': {}}
            # searchPanes_null {'species': {'0': False}, 'treatment': {}, 'topic': {}, 'method': {}, 'article_reference': {}}
            # searchPanesLast species
            # searchPanes_options {'cascade': False, 'viewCount': True, 'viewTotal': False}


            # Prepare SearchPane data
            # Panes: see list_of_search_pane_names above
            searchpanes_payload = {}

            for search_pane_column_name in list_of_search_pane_names:
                searchpanes_payload[search_pane_column_name] = []

                for unique_value_name in column_name_unique_values[search_pane_column_name]:
                    # print(f"for {search_pane_column_name} found {unique_value_name} {column_name_unique_values[search_pane_column_name][unique_value_name]}  time(s)")
                    searchpanes_payload[search_pane_column_name].append({
                        "label": unique_value_name,
                        "total": f'{column_name_unique_values[search_pane_column_name][unique_value_name]}',
                        "value": unique_value_name,
                        "count": f'{column_name_unique_values[search_pane_column_name][unique_value_name]}'
                    }, )

            # Return the data as JSON for DataTable consumption
            return JsonResponse({
                "recordsTotal": len(payload_data),  # Total record count
                "recordsFiltered": len(payload_data),  # Filtered record count (same as total if no filtering)
                'data': payload_data,  # Main payload data containing species and material details
                'searchPanes': {"options": searchpanes_payload}
                # 'property_names': serializers.serialize('json', payload_data)  # Include unique material property names
            })

        else:
            # We cannot process requests with no body,
            # because we know the DataTable will at the very least send draw and range data
            return JsonResponse({"error": "Empty request"}, status=400)
    else:
        # No support for methods that are not POST
        return JsonResponse({"error": "Invalid request method"}, status=405)


############ DOI ###########

# This view presents a form to ask for a DOI. If the entry can be resolved to a valid article, it will show that.
# If it could not be resolved, it will show an error.
@login_required
def doi_search(request):
    # Get the 'type' parameter from the URL (default to 'article' if not provided)
    content_type = request.GET.get('type', 'article')

    # If this was a POST, someone has used the submit button, check the input
    if request.method == 'POST':
        form = DOISearchForm(request.POST)
        if form.is_valid():
            # We know that the value is not empty, so we can take this DOI and ask the API about it
            possible_work = get_work_by_doi(form.cleaned_data['doi'])
            # print(possible_work)

            if possible_work and 'message' in possible_work:
                # Access the abstract from the nested 'message' dictionary
                message = possible_work['message']

                # Check if 'abstract' exists in the message dictionary
                if 'abstract' in message:
                    abstract_raw = message['abstract']  # Access the abstract directly

                    # Use BeautifulSoup to parse the abstract
                    soup = BeautifulSoup(abstract_raw, 'lxml')

                    # Find all <jats:p> tags and extract their text
                    paragraphs = soup.find_all('jats:p')
                    abstract_text = ' '.join(p.get_text() for p in paragraphs)
                else:
                    abstract_text = ''  # Set to empty if no abstract found

                # Check if 'title' exists in the message dictionary
                if 'title' in message:
                    article_title = message['title'][0]

                # Check if species name is mentioned in the abstract or title
                species_list = Species.objects.all()
                found_species = []
                for species in species_list:
                    if species.name.lower() in abstract_text.lower() or species.name.lower() in article_title.lower():
                        found_species.append(species.name)

                # If the API finds something, present this to the user
                # TODO: set the type of article/review to be imported so the Radio Button in the ChoiceField is pre-set.
                # Set the initial value for the type (article/review) in the DOIImportForm
                import_form = DOIImportForm(initial={
                    'doi': form.cleaned_data['doi'],
                    'import_type': content_type  # Pre-set the type field based on the content_type
                })

                return render(request, 'fungalmaterials/doi_import_preview.html', {
                    'form': import_form,
                    'doi_preview': possible_work,
                    'abstract_text': abstract_text,  # Pass the cleaned abstract text to the template
                    'found_species': found_species,  # Pass the found species to the template
                })
            else:
                # If the API finds nothing, let the user know this DOI didn't get us anything.
                form.add_error('doi', 'The DOI you entered is incorrect.')
    else:
        form = DOISearchForm()

    return render(request, 'fungalmaterials/doi_search_form.html', {'form': form})


# View for handling success
@login_required
@require_POST
def doi_import(request):
    form = DOIImportForm(request.POST)

    if form.is_valid():
        # Either the import is going to be OK and we set this to True, or something bad happened
        import_status = False

        # Check if we are going to treat this as an article, a review or something else
        if form.cleaned_data['import_type'] == "article":
            print("An article is going to be imported")
            import_status = import_new_article_by_doi(form.cleaned_data['doi'])
        elif form.cleaned_data['import_type'] == "review":
            print("An review is going to be imported")
            import_status = import_new_review_by_doi(form.cleaned_data['doi'])
        else:
            form.add_error('import_type', f"The import type [{form.cleaned_data['import_type']}] is not supported.")

        if import_status:
            # TODO: Fix placeholder data
            return render(request, 'fungalmaterials/doi_import_done.html',
                          {'doi_id': form.cleaned_data['doi']})
        else:
            form.add_error('doi', f"The DOI {form.cleaned_data['doi']} could not be imported.")

    else:
        form.add_error('doi', 'The DOI or Type you entered is incorrect.')

    return render(request, 'fungalmaterials/doi_import_preview.html', {'form': form})


############ ABOUT ###########

def about(request):
    # combination_list = [
    #     {
    #         'method': article['method__name'],
    #         'topic': article['topic__name']
    #     }
    #     for article in Article.objects.select_related('method', 'topic')
    #     # This filters out articles with method or topic is None
    #     .filter(method__isnull=False, topic__isnull=False)
    #     .values('method__name', 'topic__name')
    # ]

    # # Use function to generate sankey figure
    # sankey_fig = generate_sankey(combination_list)


    def add_missing_years(years, data):
        all_years = []  # Create a list to store all years, including missing ones
        data_with_missing = []  # Create a list to store the data for all years, including missing ones
        if years:  # Check if there are any years
            start = int(years[0])  # Get the start year and the end year
            end = int(years[-1])
            year_counts = defaultdict(int)  # Create a defaultdict to store the counts for each year
            for count in data:  # Loop through the data and store the count for each year in the defaultdict
                year_counts[int(count['year'])] = count['year__count']
            for year in range(start,
                              end + 1):  # Loop through the range of years and add each year to the list of all_years and its count (if available) or 0 to the list of data_with_missing
                all_years.append(str(year))
                data_with_missing.append(year_counts.get(year, 0))
        return all_years, data_with_missing  # Return the lists of all_years and data_with_missing


    # Articles chart
    articles_year_order = Article.objects.all().values_list('year', flat=True).exclude(approved=False).order_by('year').distinct()
    articles_year_order = list(articles_year_order)
    articles_year_count = Article.objects.values('year').annotate(Count('year')).exclude(approved=False).order_by('year')
    articles_year_order, articles_year_count= add_missing_years(articles_year_order, articles_year_count)  # Call the function to add missing years and add their counts as 0 to the data
    articles_year_count = list(articles_year_count)

    # Reviews chart
    reviews_year_order = Review.objects.all().values_list('year', flat=True).exclude(approved=False).order_by('year').distinct()
    reviews_year_order = list(reviews_year_order)
    reviews_year_count = Review.objects.values('year').annotate(Count('year')).exclude(approved=False).order_by('year')
    reviews_year_order, reviews_year_count= add_missing_years(reviews_year_order, reviews_year_count)  # Call the function to add missing years and add their counts as 0 to the data
    reviews_year_count = list(reviews_year_count)

    context = {
        # 'sankey_fig': sankey_fig,
        # 'combination_list': combination_list,
        'articles_year_order': articles_year_order,
        'articles_year_count': articles_year_count,
        'reviews_year_order': reviews_year_order,
        'reviews_year_count': reviews_year_count,
    }
    return render(request, "fungalmaterials/about.html", context)


############ TEST PAGE ###########

@login_required
def test(request):
    topics = Topic.objects.all()
    methods = Method.objects.all()

    context = {
        'topics': topics,
        'methods': methods,
    }
    return render(request, "fungalmaterials/test.html", context)
