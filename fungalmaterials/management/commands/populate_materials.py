from django.core.management.base import BaseCommand
from django.db.models.functions import Substr

from fungalmaterials.doi import import_new_article_by_doi, get_work_by_doi
from fungalmaterials.models import Material, Species, Method, Article, Substrate, PropertyName, Unit, Property


class Command(BaseCommand):
    help = 'Populate the Materials model with default data if not already present'

    def handle(self, *args, **kwargs):
        # List of DOIs to add

        materials = [
            {
                "species": "Schizophyllum commune",
                "substrates": "SCMM",
                "article_doi": "https://doi.org/10.1016/j.biortech.2024.130807",
                "method": "LSF",
                "treatment": "Control",
                "properties": [
                    {
                        "value": "587",
                        "name": "Density",
                        "unit": "kg/m3"
                    },
                    {
                        "value": "1.5",
                        "name": "Strain",
                        "unit": "%"
                    },
                ]
            },

            {
                "species": "Schizophyllum commune",
                "substrates": "SCMM",
                "article_doi": "https://doi.org/10.1038/s42003-020-1064-4",
                "method": "LSF",
                "treatment": "8% glycerol",
                "properties": [
                    {
                        "value": "1262",
                        "name": "Density",
                        "unit": "kg/m3"
                    },
                    {
                        "value": "14.9",
                        "name": "Strain",
                        "unit": "%"
                    },
                ]
            },

            {
                "species": "Pleurotus ostreatus",
                "substrates": "MEB",
                "article_doi": "https://doi.org/10.1016/j.fgb.2024.103913",
                "method": "SSF",
                "treatment": "",
                "properties": [
                    {
                        "value": "1000",
                        "name": "Density",
                        "unit": "kg/m3"
                    },
                    {
                        "value": "10",
                        "name": "Strain",
                        "unit": "%"
                    },
                ]
            },

            {
                "species": "Pleurotus ostreatus",
                "substrates": "MEB",
                "article_doi": "https://doi.org/10.1016/j.heliyon.2024.e36263",
                "method": "SSF",
                "treatment": "",
                "properties": [
                    {
                        "value": "543",
                        "name": "Density",
                        "unit": "kg/m3"
                    },
                    {
                        "value": "23.7",
                        "name": "Strain",
                        "unit": "%"
                    },
                ]
            },

            {
                "species": "Ganoderma lucidum",
                "substrates": "MEB",
                "article_doi": "https://doi.org/10.1016/j.micres.2024.127736",
                "method": "SSF",
                "treatment": "",
                "properties": [
                    {
                        "value": "1200",
                        "name": "Density",
                        "unit": "kg/m3"
                    },
                    {
                        "value": "5",
                        "name": "Strain",
                        "unit": "%"
                    },
                    {
                        "value": "10",
                        "name": "Stress",
                        "unit": "MPa"
                    },
                ]
            },
        ]

        for mat in materials:
            # Check if the prerequisites exist:
            try:
                import_new_article_by_doi(mat.get("article_doi"))
                self.stdout.write(self.style.SUCCESS(f'Imported an article for material reference: {mat.get("article_doi")}'))
            except Exception as e:
                self.stdout.write(self.style.SUCCESS(f'Article for material reference already present: {mat.get("article_doi")}'))


            material, created = Material.objects.update_or_create(
                article = Article.objects.get(doi=mat.get("article_doi")),
                treatment = mat.get("treatment")
            )


            # Substrate / Material: upsert ( list )
            substrate, created = Substrate.objects.update_or_create(
                name  = mat.get("substrates")
            )
            material.substrates.set([substrate])

            # Species ( list ) # This field must be pre-loaded using the other populate commands
            material.species.set([Species.objects.get(name__iexact=mat.get("species"))])

            # Method ( list ) # This field must be pre-loaded using the other populate commands
            material.method.set([Method.objects.get(name__iexact=mat.get("method"))])


            # Properties
            for prop in mat.get("properties"):
                # Check if the name/type of property exists
                property_name, created = PropertyName.objects.update_or_create(
                    name=prop.get("name")
                )

                # Check if the unit exists
                property_unit, created = Unit.objects.update_or_create(
                    symbol=prop.get("unit")
                )

                # Create a new property with the correct value
                material_property, created = Property.objects.update_or_create(
                    value=prop.get("value"),
                    unit=property_unit,
                    name=property_name,
                    material=material
                )

                material_property.save()

            material.save()

            if created:
                self.stdout.write(self.style.SUCCESS(f'Successfully created: {material.id}'))
            else:
                self.stdout.write(self.style.SUCCESS(f'Material updated/preserved: {material.id}'))

        self.stdout.write(self.style.SUCCESS('Material population completed!'))
