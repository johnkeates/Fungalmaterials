from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import datetime
import calendar


# Date
class Date(models.Model):
	current_year = datetime.now().year
	year = models.PositiveIntegerField(help_text="Year published online",
		null=True, validators=[MinValueValidator(1850), MaxValueValidator(current_year + 1)])
	month = models.PositiveIntegerField(help_text="Month published online",
		blank=True, null=True, validators=[MinValueValidator(1), MaxValueValidator(12)])
	day = models.PositiveIntegerField(help_text="Day published online",
		blank=True, null=True, validators=[MinValueValidator(1), MaxValueValidator(31)])

	class Meta:
		abstract = True 
	
	def get_month_name(self):
		if self.month:
			return calendar.month_name[self.month]
		return ''


# Author
class Author(models.Model):
	name = models.CharField(max_length=50)
	family = models.CharField(max_length=100, null=True)
	affiliation = models.CharField(max_length=100, blank=True)

	class Meta:
		unique_together = ['name', 'family']

	def __str__(self):
		return f"{self.name} {self.family}"


# Species
class Species(models.Model):
	name = models.CharField(max_length=100, unique=True)
	alternative_names = models.TextField(blank=True, help_text="Comma-separated common names or synonyms")
	phylum_choice = (
		('Basidiomycota','Basidiomycota'),
		('Ascomycota','Ascomycota'),
		('Blastocladiomycota','Blastocladiomycota'),
		('Mycoromycota','Mycoromycota'),
		('Opisthosporidia','Opisthosporidia'))
	phylum = models.CharField(max_length=20, choices=phylum_choice, blank=True)

	class Meta:
		verbose_name_plural = "Species" 

	def __str__(self):
		return self.name


# Substrate 
class Substrate(models.Model):
	name = models.CharField("Substrate/Medium", max_length=100, unique=True)

	def __str__(self):
		return self.name


# Topic
class Topic(models.Model):
	name = models.CharField(max_length=20, unique=True)

	def __str__(self):
		return self.name


# Method
class Method(models.Model):
	name = models.CharField(max_length=20, unique=True)

	def __str__(self):
		return self.name


# Article
class Article(Date):
	title = models.CharField(max_length=300, unique=True)
	authors = models.ManyToManyField('Author', through='ArticleAuthorship', verbose_name="Author(s)")
	journal = models.CharField(max_length=100, blank=True)
	doi = models.URLField(max_length=100, unique=True, null=True, blank=True)
	# pdf = models.FileField(blank=True, null=True)
	abstract = models.TextField(max_length=2000, blank=True)
	topic = models.ManyToManyField(Topic, blank=True)
	approved = models.BooleanField('Approved',default=False)

	class Meta:
		unique_together = ['title', 'doi']

	def __str__(self):
		return self.title


# Review
class Review(Date):
	title = models.CharField(max_length=300, unique=True)
	authors = models.ManyToManyField('Author', through='ReviewAuthorship', verbose_name="Author(s)")
	journal = models.CharField(max_length=100, blank=True)
	doi = models.URLField(max_length=100, unique=True, null=True, blank=True)
	# pdf = models.FileField(blank=True, null=True)
	abstract = models.TextField(max_length=2000, blank=True)
	topic = models.ManyToManyField(Topic, blank=True)
	approved = models.BooleanField('Approved',default=False)

	class Meta:
		unique_together = ['title', 'doi']

	def __str__(self):
		return self.title


# Article-Author relationship
class ArticleAuthorship(models.Model):
	author = models.ForeignKey(Author, on_delete=models.CASCADE)
	article = models.ForeignKey(Article, on_delete=models.CASCADE)
	sequence_choice = (
		('first', 'first'),
		('additional', 'additional')
	)
	sequence = models.CharField(max_length=20, choices=sequence_choice, blank=True)

	class Meta:
		unique_together = ['author', 'article', 'sequence']

	def __str__(self):
		return self.author.name


# Review-Author relationship
class ReviewAuthorship(models.Model):
	author = models.ForeignKey(Author, on_delete=models.CASCADE)
	review = models.ForeignKey(Review, on_delete=models.CASCADE)
	sequence_choice = (
		('first', 'first'),
		('additional', 'additional')
	)
	sequence = models.CharField(max_length=20, choices=sequence_choice, blank=True)
	affiliation = models.CharField(max_length=100, blank=True)

	class Meta:
		unique_together = ['author', 'review', 'sequence']

	def __str__(self):
		return self.author.name


# Unit
class Unit(models.Model):
	symbol = models.CharField(max_length=10, unique=True, help_text="Symbol of the unit (e.g. g/cm³)")
	name = models.CharField(max_length=50, blank=True, help_text="Full name of the unit (e.g. grams per cubic centimeter)")

	def __str__(self):
		return self.symbol


# Material
	# A material is connected to exactly one article, but multiple articles might describe identical materials
	# The treatment of the material is generally described in the article
	# The species as well, but there might be multiple, same goes for substrates and methods
class Material(models.Model):
	article = models.ForeignKey(Article, on_delete=models.CASCADE)
	treatment = models.CharField(max_length=50, blank=True)
	species = models.ManyToManyField(Species, blank=True)
	substrates = models.ManyToManyField(Substrate, blank=True, verbose_name="Substrate/Medium")
	method = models.ManyToManyField(Method, blank=True)

	class Meta:
		verbose_name_plural = "Materials"
		unique_together = ['article', 'treatment']


# Property
class Property(models.Model):
	value = models.FloatField(help_text="Measured value of the property")
	name = models.CharField(max_length=50, unique=True)
	unit = models.ForeignKey(Unit, on_delete=models.CASCADE)
	material = models.ForeignKey(Material, on_delete=models.CASCADE)

	def __str__(self):
		return self.value

	class Meta:
		verbose_name_plural = "Properties"

