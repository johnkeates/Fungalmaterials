# Generated by Django 4.2.16 on 2024-09-29 10:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("fungalmaterials", "0028_alter_review_abstract"),
    ]

    operations = [
        migrations.AlterField(
            model_name="review",
            name="doi",
            field=models.URLField(blank=True, max_length=100, null=True, unique=True),
        ),
    ]
