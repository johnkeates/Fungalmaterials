# Generated by Django 4.2.16 on 2024-09-06 12:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0010_alter_review_title_alter_review_year_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='substrate',
            field=models.ManyToManyField(blank=True, to='main.substrate', verbose_name='Substrate/Medium'),
        ),
    ]