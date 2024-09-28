def AuthorSeparation(authors):
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