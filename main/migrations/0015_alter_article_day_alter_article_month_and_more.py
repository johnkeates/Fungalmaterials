# Generated by Django 4.2.16 on 2024-09-07 08:10

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0014_alter_article_year_alter_review_year'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='day',
            field=models.PositiveIntegerField(blank=True, help_text='Day published online', null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(31)]),
        ),
        migrations.AlterField(
            model_name='article',
            name='month',
            field=models.PositiveIntegerField(blank=True, help_text='Month published online', null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(12)]),
        ),
        migrations.AlterField(
            model_name='review',
            name='day',
            field=models.PositiveIntegerField(blank=True, help_text='Day published online', null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(31)]),
        ),
        migrations.AlterField(
            model_name='review',
            name='month',
            field=models.PositiveIntegerField(blank=True, help_text='Month published online', null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(12)]),
        ),
    ]
