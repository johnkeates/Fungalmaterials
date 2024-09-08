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
	name = models.CharField(max_length=50, unique=True, 
		help_text="Please enter author names as: last name, first name (e.g. Smith, Jane)")

	def __str__(self):
		return self.name


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
	title = models.CharField(max_length=300)
	authors = models.ManyToManyField(Author, blank=True, verbose_name="Author(s)", 
		help_text="Please enter author names as: last name, first name (e.g. Smith, Jane)")
	journal = models.CharField(max_length=100, blank=True)
	doi = models.URLField(max_length=100, unique=True, blank=True)
	# pdf = models.FileField(blank=True, null=True)
	# abstract = models.TextField(max_length=1500, blank=True)
	species = models.ManyToManyField(Species, blank=True)
	substrate = models.ManyToManyField(Substrate, blank=True, verbose_name="Substrate/Medium")
	topic = models.ManyToManyField(Topic, blank=True)
	method = models.ManyToManyField(Method, blank=True)
	approved = models.BooleanField('Approved',default=False)

	class Meta:
		unique_together = ['title', 'doi']

	def __str__(self):
		return self.title


# Review
class Review(Date):
	title = models.CharField(max_length=300)
	authors = models.ManyToManyField(Author, blank=True, verbose_name="Author(s)", 
		help_text="Please enter author names as: last name, first name (e.g. Smith, Jane)")
	journal = models.CharField(max_length=100, blank=True)
	doi = models.URLField(max_length=100, unique=True, blank=True)
	# pdf = models.FileField(blank=True, null=True)
	# abstract = models.TextField(max_length=1500, blank=True)
	topic = models.ManyToManyField(Topic, blank=True)
	approved = models.BooleanField('Approved',default=False)

	class Meta:
		unique_together = ['title', 'doi']

	def __str__(self):
		return self.title


# Property
class Property(models.Model):
	name = models.CharField(max_length=50, unique=True)

	def __str__(self):
		return self.name

	class Meta:
		verbose_name_plural = "Properties" 


# Unit
class Unit(models.Model):
	symbol = models.CharField(max_length=10, unique=True, help_text="Symbol of the unit (e.g. g/cm³)")
	name = models.CharField(max_length=50, blank=True, help_text="Full name of the unit (e.g. grams per cubic centimeter)")

	def __str__(self):
		return self.symbol


# Material property
class MaterialProperty(models.Model):
	article = models.ForeignKey(Article, on_delete=models.CASCADE)
	species = models.ForeignKey(Species, on_delete=models.CASCADE)
	substrate = models.ForeignKey(Substrate, on_delete=models.CASCADE)
	treatment = models.CharField(max_length=50, blank=True)
	material_property = models.ForeignKey(Property, on_delete=models.CASCADE)
	value = models.FloatField(help_text="Measured value of the property")
	unit = models.ForeignKey(Unit, on_delete=models.CASCADE)

	class Meta:
		verbose_name_plural = "Material properties" 

