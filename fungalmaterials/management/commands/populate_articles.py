from django.core.management.base import BaseCommand

from fungalmaterials.doi import import_new_article_by_doi


class Command(BaseCommand):
    help = 'Populate the Article model with default data if not already present'

    def handle(self, *args, **kwargs):
        # List of DOIs to add
        dois = ["https://doi.org/10.1007/s00203-024-04087-0",
                "https://doi.org/10.1016/j.biortech.2024.130807",
                "https://doi.org/10.1016/j.cofs.2024.101169",
                "https://doi.org/10.1016/j.fgb.2024.103913",
                "https://doi.org/10.1016/j.fgb.2024.103925",
                "https://doi.org/10.1016/j.heliyon.2024.e36263",
                "https://doi.org/10.1016/j.ijbiomac.2024.134326",
                "https://doi.org/10.1016/j.micres.2024.127736",
                "https://doi.org/10.1016/j.micres.2024.127929",
                "https://doi.org/10.1016/j.mtcomm.2024.109784",
                "https://doi.org/10.1146/annurev-micro-041522-092522",
                "https://doi.org/10.1186/s43008-024-00155-8",
                "https://doi.org/10.33540/2435",
                "https://doi.org/10.33540/2484",
				"https://doi.org/10.1038/s42003-020-1064-4"]

        for doi in dois:
            try:
                import_new_article_by_doi(doi)
                self.stdout.write(self.style.SUCCESS(f'Successfully imported: {doi}'))

            except Exception as e:
                self.stdout.write(self.style.WARNING(f"The DOI {doi} could not be imported. It might already be present."))

        self.stdout.write(self.style.SUCCESS('Article population completed!'))
