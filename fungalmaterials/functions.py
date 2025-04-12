from fungalmaterials.models import Article

def authorship_string(article: Article):
	# Load all authorships for the supplied article
	authorships = article.articleauthorship_set.all()

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

def author_separation(authors):
	# Convert the QuerySet to a list
	authors = list(authors)

	# Check the number of authors
	x = len(authors)

	# Handle different cases for the number of authors
	if x == 0:
		return ""
	if x == 1:
		return f"{authors[0].name} {authors[0].family}"
	elif x == 2:
		return f"{authors[0].name} {authors[0].family} & {authors[1].name} {authors[1].family}"
	else:
		# Join all authors except the last one with ', ', then add the last author with ' & '
		result = ', '.join([f"{author.name} {author.family}" for author in authors[:-1]]) + f" & {authors[-1].name} {authors[-1].family}"
		return result