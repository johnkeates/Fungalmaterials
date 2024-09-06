from django.db import models


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
class Article(models.Model):
    title = models.CharField(max_length=300)
    year = models.PositiveIntegerField()
    authors = models.TextField(help_text="Comma-separated list of authors", blank=True)
    journal = models.CharField(max_length=100, blank=True)
    doi = models.URLField(max_length=100, unique=True, blank=True)
    species = models.ManyToManyField(Species, blank=True)
    substrate = models.ManyToManyField(Substrate, blank=True)
    topic = models.ManyToManyField(Topic, blank=True)
    method = models.ManyToManyField(Method, blank=True)
    approved = models.BooleanField('Approved',default=False)

    def __str__(self):
        return self.title


# Review
class Review(models.Model):
    title = models.CharField(max_length=300, unique=True)
    year = models.PositiveIntegerField()
    authors = models.TextField(help_text="Comma-separated list of authors", blank=True)
    journal = models.CharField(max_length=100, blank=True)
    doi = models.URLField(max_length=100, unique=True, blank=True)
    topic = models.ManyToManyField(Topic, blank=True)
    approved = models.BooleanField('Approved',default=False)



# Property
# class Property(models.Model):
#     name = models.CharField(max_length=100)

#     def __str__(self):
#         return self.type


# Material property
# class MaterialProperty(models.Model):
#     article = models.ForeignKey('Article', on_delete=models.CASCADE)
#     species = models.ForeignKey('Species', on_delete=models.CASCADE)
#     substrate = models.ForeignKey('Substrate', on_delete=models.CASCADE)
#     treatment = models.CharField(max_length=255, blank=True)
#     property = models.ForeignKey(Property, on_delete=models.CASCADE)
#     value = models.FloatField(help_text="Measured value of the property")
#     unit = models.CharField(max_length=50, help_text="Unit of the measured property, e.g., g/cm³, MPa, etc.")

