# Generated by Django 4.2.16 on 2024-09-07 17:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fungalmaterials', '0017_author_remove_article_authors_remove_review_authors_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='author',
            name='name',
            field=models.CharField(help_text='Please enter author names as: last name, first name (e.g. Smith, Jane)', max_length=50, unique=True),
        ),
    ]