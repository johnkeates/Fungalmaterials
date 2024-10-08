# Generated by Django 4.2.16 on 2024-09-22 13:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fungalmaterials', '0022_article_abstract_review_abstract'),
    ]

    operations = [
        migrations.AddField(
            model_name='author',
            name='affiliation',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='author',
            name='family',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='author',
            name='sequence',
            field=models.CharField(blank=True, choices=[('first', 'first'), ('additional', 'additional')], max_length=20),
        ),
        migrations.AlterField(
            model_name='article',
            name='authors',
            field=models.ManyToManyField(blank=True, to='fungalmaterials.author', verbose_name='Author(s)'),
        ),
        migrations.AlterField(
            model_name='author',
            name='name',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name='review',
            name='authors',
            field=models.ManyToManyField(blank=True, to='fungalmaterials.author', verbose_name='Author(s)'),
        ),
        migrations.AlterUniqueTogether(
            name='author',
            unique_together={('name', 'family')},
        ),
    ]
