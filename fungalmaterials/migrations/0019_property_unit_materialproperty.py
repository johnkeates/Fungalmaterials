# Generated by Django 4.2.16 on 2024-09-08 13:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('fungalmaterials', '0018_alter_author_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Property',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Unit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Full name of the unit (e.g. grams per cubic centimeter', max_length=50, unique=True)),
                ('symbol', models.CharField(blank=True, help_text='Symbol of the unit (e.g. g/cm³)', max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='MaterialProperty',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('treatment', models.CharField(blank=True, max_length=50)),
                ('value', models.FloatField(help_text='Measured value of the property')),
                ('article', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='fungalmaterials.article')),
                ('material_property', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='fungalmaterials.property')),
                ('species', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='fungalmaterials.species')),
                ('substrate', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='fungalmaterials.substrate')),
                ('unit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='fungalmaterials.unit')),
            ],
        ),
    ]