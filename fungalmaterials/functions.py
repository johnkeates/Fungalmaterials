from django.db.models import QuerySet
from fungalmaterials.models import Article, Review


def authorship_string(authorships: QuerySet):
	# Load two separate sets, one for 'first', one for the others
	first_authorships = authorships.filter(sequence="first")
	additional_authorships = authorships.filter(sequence="additional")

	# Collect all authors in a list
	list_of_authors = []

	# We know these are not frequent or large lists so we can do a naive re-processing twice

	# First, grab all the 'first' authors. If there is no 'first' author, this code skips it safely
	for authorship in first_authorships:
		list_of_authors.append(authorship.author)

	# Next, grab all the 'additional' authors. If there is no 'additional' author, this code skips it safely
	for authorship in additional_authorships:
		list_of_authors.append(authorship.author)

	# If there are no authors, we yield an empty string, so we prepare that here:
	authors = ""

	# If there is exactly one author after that previous process, we just return that one
	if len(list_of_authors) == 1:
		authors = list_of_authors.pop().__str__()

	# If there is more than one, we reverse-build the string:
	if len(list_of_authors) > 1:
		# We use an & for the last author, so we cut that last one and store it here
		last_author = list_of_authors.pop()

		# All the others, we join together with a comma. If the list only has 1 element, this will result in just that
		authors = ", ".join(str(author) for author in list_of_authors)

		# And then we glue that last one back on to the list.
		# The previous actions will have either yielded a comma-separated string, or a string with a single author.
		authors = authors + " & " + last_author.__str__()

	return authors


# Article variant to get a nice list of authors in a string
def authorship_string_article(article: Article):
	# Load all authorships for the supplied article
	authorships = article.articleauthorship_set.all()
	return authorship_string(authorships)

# Review variant to get a nice list of authors in a string
def authorship_string_review(review: Review):
	# Load all authorships for the supplied review
	authorships = review.reviewauthorship_set.all()
	return authorship_string(authorships)