from django.core.management.base import BaseCommand
from django.db import transaction
from fungalmaterials.doi import import_new_review_by_doi
from fungalmaterials.models import Topic, Review


class Command(BaseCommand):
    help = 'Populate the Review model with default data if not already present'

    def handle(self, *args, **kwargs):
        # List of DOIs to add
        # Topics: Pure, Composite, Nanopaper, 3D, Amadou, Living, Electrical
        dois_with_topics = {"https://doi.org/10.1186/s40694-022-00134-x": ["Pure", "Composite"],
                            "https://doi.org/10.3390/polym14010145": ["Composite"],
                            "https://doi.org/10.1016/j.jclepro.2022.131659": ["Composite"],
                            "https://doi.org/10.3390/ma15186283": ["Composite"],
                            "https://doi.org/10.1155/2022/8401528": ["Composite"],
                            "https://doi.org/10.3389/fbioe.2018.00137": [],
                            "https://doi.org/10.3389/fbioe.2022.1067869": ["Composite"],
                            "https://doi.org/10.1080/13511610.2022.2110453": ["Composite"],
                            "https://doi.org/10.1007/s10853-023-08214-y": ["Pure", "Composite"],
                            "https://doi.org/10.1128/msphere.00681-22": [],
                            "https://doi.org/10.3390/jof8080842": ["Composite"],
                            "https://doi.org/10.1021/acs.jafc.2c08828": ["Composite"],
                            "https://doi.org/10.1042/bio_2023_120": ["Pure", "Composite"],
                            "https://doi.org/10.1016/j.mtbio.2023.100560": ["Pure", "Composite"],
                            "https://doi.org/10.1016/j.mtcomm.2023.106477": [],
                            "https://doi.org/10.3389/fbioe.2023.1204861": ["Pure", "Composite"],
                            "https://doi.org/10.7717/peerj-matsci.31": [],
                            "https://doi.org/10.1002/9781394175406.ch16": [],
                            "https://doi.org/10.1016/j.susmat.2023.e00724": ["Pure", "Nanopaper", "Amadou"],
                            "https://doi.org/10.1002/adsu.202300305": ["Composite"],
                            "https://doi.org/10.1002/gch2.202300140": ["Pure", "Composite"],
                            "https://doi.org/10.1016/j.biteb.2023.101456": ["Composite"],
                            "https://doi.org/10.7841/ksbbj.2023.38.3.153": ["Pure", "Composite"],
                            "https://doi.org/10.18848/2325-1379/CGP/v18i02/37-62": ["Composite"],
                            "https://doi.org/10.3390/jof10030183": ["Pure"],
                            "https://doi.org/10.1116/6.0003441": ["Pure", "Composite"],
                            "https://doi.org/10.1002/bbb.2620": ["Composite"],
                            "https://doi.org/10.1016/j.jclepro.2024.141859": ["Composite"],
                            "https://doi.org/10.1002/gch2.202300197": ["Composite"],
                            "https://doi.org/10.3390/biomimetics9060337": ["Composite"],
                            "https://doi.org/10.1002/gch2.202400104": ["Living", "Electrical", "Composite"],
                            "https://doi.org/10.3390/f15071230": [],
                            "https://doi.org/10.1177/14777606241252702": ["Composite"],
                            "https://doi.org/10.3390/bioengineering11080840": ["3D", "Composite"],
                            "https://doi.org/10.1007/s44174-024-00206-z": [],
                            "https://doi.org/10.1007/s43939-024-00084-8": ["Composite"],
                            "https://doi.org/10.1155/2023/1629174": ["Pure"],
                            "https://doi.org/10.3389/ffunb.2023.1135263": [],
                            "https://doi.org/10.1016/j.tibtech.2021.03.002": ["Pure", "Nanopaper", "Amadou"],
                            "https://doi.org/10.1038/s41893-020-00606-1": ["Pure", "Nanopaper"],
                            "https://doi.org/10.1016/j.matdes.2019.108397": ["Composite"],
                            "https://doi.org/10.3390/md18010064": ["Pure", "Nanopaper"],
                            "https://doi.org/10.1021/acs.biomac.9b01141": ["Pure", "Nanopaper"],
                            "https://doi.org/10.1002/gch2.202400315": [],
                            }

        for doi, topics in dois_with_topics.items():
            try:
                with transaction.atomic():
                    # Import the review data for the given DOI
                    import_success = import_new_review_by_doi(doi)

                    # If import was successful, retrieve the review by DOI
                    if import_success:
                        review = Review.objects.get(doi=doi)

                        # Assign topics to the review
                        for topic_name in topics:
                            topic, _ = Topic.objects.get_or_create(name=topic_name)
                            review.topic.add(topic)

                        review.save()
                        self.stdout.write(self.style.SUCCESS(f'Successfully imported and updated topics for: {doi}'))
                    else:
                        self.stdout.write(self.style.WARNING(f"The DOI {doi} could not be imported. It might already be present."))

            except Exception as e:
                self.stdout.write(self.style.WARNING(f"Error importing DOI {doi}: {str(e)}"))

        self.stdout.write(self.style.SUCCESS('Review population with topics completed!'))
