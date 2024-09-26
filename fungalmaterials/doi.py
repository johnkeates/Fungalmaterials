from habanero import Crossref
from fungalmaterials.models import Article, Author, ArticleAuthorship


# This tries to get a single work, but the API will always think about it in terms of lists
def get_work_by_doi(doi):
	# Very basic input check, DOI tends to be longer.
	if len(doi) < 3:
		return None

	cr = Crossref(mailto="j.g.vandenbrandhof@uu.nl")
	return cr.works(ids=[doi])

# This tries to get a work and then create an Article, Authors and their Authorship for the article.
# Currently hard-crashes if the article already exists and doesn't really check pre-existing authorship either.
def import_new_article_by_doi(doi):
	# Blind import: we make a lot of assumptions about the arrays, like assuming there is always something at index 0.
	# TODO: it would be more robust if we checked the array length or checked the results before setting the model data.
	work_message = get_work_by_doi(doi)
	work = work_message['message']

	article = Article()

	article.title = work['title'][0]
	article.abstract = work['abstract']
	article.year = work['published']['date-parts'][0][0]
	article.month = work['published']['date-parts'][0][1]
	article.day = work['published']['date-parts'][0][2]
	article.journal = work['container-title'][0]
	article.doi = work['DOI']
	article.save()

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

	return True
