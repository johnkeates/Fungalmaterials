# Generated by Django 4.2.16 on 2024-12-03 20:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fungalmaterials', '0005_alter_article_abstract'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='material',
            unique_together=set(),
        ),
    ]
