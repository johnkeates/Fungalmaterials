from habanero import Crossref
import re
from bs4 import BeautifulSoup
from fungalmaterials.models import Article, Author, ArticleAuthorship, Review, ReviewAuthorship, Species, Material


# This tries to get a single work, but the API will always think about it in terms of lists
def get_work_by_doi(doi):
	# Very basic input check, DOI tends to be longer.
	if len(doi) < 3:
		return None

	cr = Crossref(mailto="j.g.vandenbrandhof@uu.nl")
	return cr.works(ids=[doi])


# Clean abstract from
def clean_abstract(abstract_raw):
	# Parse with BeautifulSoup
	soup = BeautifulSoup(abstract_raw, 'lxml')
	paragraphs = soup.find_all('jats:p')
	abstract_text = ' '.join(p.get_text() for p in paragraphs)

	# Remove LaTeX artifacts and convert scientific notations
	abstract_text = re.sub(r'\\hspace\{[^}]+\}', ' ', abstract_text)     # Remove \hspace commands
	abstract_text = re.sub(r'\\text\{([^}]+)\}', r'\1', abstract_text)    # Extract content in \text{}
	abstract_text = re.sub(r'\{([^}]+)\^\{-2\}\}', r'\1 per m²', abstract_text)  # Convert {m^{-2}} to "per m²"
	abstract_text = re.sub(r'\s+', ' ', abstract_text)  # Collapse multiple spaces

	# Handle remaining {} by removing them
	abstract_text = re.sub(r'[{}]', '', abstract_text)

	return abstract_text.strip()


# This tries to get a work and then create an Article, Authors and their Authorship for the article.
# Currently hard-crashes if the article already exists and doesn't really check pre-existing authorship either.
def import_new_article_by_doi(doi):
	# Blind import: we make a lot of assumptions about the arrays, like assuming there is always something at index 0.
	# TODO: it would be more robust if we checked the array length or checked the results before setting the model data.
	work_message = get_work_by_doi(doi)
	work = work_message['message']

	article = Article()

	# Check title
	if 'title' in work:
		if len(work['title']) > 0:
			article.title = work['title'][0]
	
	# Check if exists in work dictionary
	if 'abstract' in work:
		abstract_raw = work['abstract']
		article.abstract = clean_abstract(abstract_raw)

	# Check year, month and day
	if 'published' in work and 'date-parts' in work['published']:
		date_parts = work['published']['date-parts'][0]

		if len(date_parts) > 0:  # Ensure the year exists
			article.year = date_parts[0]
		if len(date_parts) > 1:  # Ensure the month exists
			article.month = date_parts[1]
		if len(date_parts) > 2:  # Ensure the day exists
			article.day = date_parts[2]

	# Check journal name
	if 'container-title' in work:
		if len(work['container-title']) > 0:
			article.journal = work['container-title'][0]

	# Check DOI
	doi_value = work['DOI']
	if not doi_value.startswith("https://doi.org/"):
		doi_value = f"https://doi.org/{doi_value}"
	article.doi = doi_value

	# Set the Approved field to True
	article.approved = True

	# Save model entries
	article.save()

	# Check author(s)
	if 'author' in work:
		# Process authors
		for author_entry in work['author']:
			author, created = Author.objects.get_or_create(
				name=author_entry['given'], family=author_entry['family']
			)

			authorship = ArticleAuthorship()
			authorship.article = article
			authorship.author = author

			if author_entry['sequence'] == "additional":
				authorship.sequence = "additional"

			if author_entry['sequence'] == "first":
				authorship.sequence = "first"

			authorship.save()

	# Check if species is mentioned in title or abstract
	# If so, add the species to the material object linked to the article
	species_list = Species.objects.all()
	# Empty set to make sure each found species is added indidivually as new material
	found_species = set()

	for species in species_list:
		# Check if the species name is found in the article title or abstract
		if species.name.lower() in article.title.lower() or species.name.lower() in article.abstract.lower():
			if species not in found_species:
				# Create a new Material for the species
				material = Material(article=article)
				material.save() 
				material.species.add(species)  	# Add the species to the ManyToManyField
				found_species.add(species) 		# Mark species as added
				print(f"Species {species} found in the title or abstract and added as material!")

	return True


# This tries to get a work and then create an Article, Authors and their Authorship for the article.
# Currently hard-crashes if the article already exists and doesn't really check pre-existing authorship either.
def import_new_review_by_doi(doi):
	# Blind import: we make a lot of assumptions about the arrays, like assuming there is always something at index 0.
	# TODO: it would be more robust if we checked the array length or checked the results before setting the model data.
	work_message = get_work_by_doi(doi)
	work = work_message['message']

	review = Review()

	# Check title
	if 'title' in work:
		review.title = work['title'][0]

	# Check if exists in work dictionary
	if 'abstract' in work:
		abstract_raw = work['abstract']
		review.abstract = clean_abstract(abstract_raw)

	# Check year, month and day
	if 'published' in work and 'date-parts' in work['published']:
		date_parts = work['published']['date-parts'][0]

		if len(date_parts) > 0:  # Ensure the year exists
			review.year = date_parts[0]
		if len(date_parts) > 1:  # Ensure the month exists
			review.month = date_parts[1]
		if len(date_parts) > 2:  # Ensure the day exists
			review.day = date_parts[2]

	# Check journal name
	if 'container-title' in work:
		review.journal = work['container-title'][0]

	# Check DOI
	doi_value = work['DOI']
	if not doi_value.startswith("https://doi.org/"):
		doi_value = f"https://doi.org/{doi_value}"
	review.doi = doi_value

	# Set the Approved field to True
	review.approved = True

	# Save model entries
	review.save()

	# Check author(s)
	if 'author' in work:
		# Process authors
		for author_entry in work['author']:
			author, created = Author.objects.get_or_create(
				name=author_entry['given'], family=author_entry['family']
			)

			authorship = ReviewAuthorship()
			authorship.review = review
			authorship.author = author

			if author_entry['sequence'] == "additional":
				authorship.sequence = "additional"

			if author_entry['sequence'] == "first":
				authorship.sequence = "first"

			authorship.save()

	return True
