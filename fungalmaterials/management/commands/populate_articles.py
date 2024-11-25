from django.core.management.base import BaseCommand
from django.db import transaction
from fungalmaterials.doi import import_new_article_by_doi
from fungalmaterials.models import Method, Topic, Article, Species, Material


class Command(BaseCommand):
    help = 'Populate the Article model with default data if not already present'

    def handle(self, *args, **kwargs):
        # List of DOIs to add
        # Topics: Pure, Composite, Nanopaper, 3D, Amadou, Living, Electrical, Adhesion
        # Methods: FB, LSF, SSF 
        dois = {
            "https://doi.org/10.1016/j.mtcomm.2024.109784": (["Pure", "Living"], ["LSF"]),
            "https://doi.org/10.3390/jof8030317": (["Pure"], ["SSF"]),
            "https://doi.org/10.3390/biomimetics7020057": (["Composite"], ["SSF"]),
            "https://doi.org/10.3390/jof7121008": (["Pure"], [""]),
            "https://doi.org/10.3390/su132111573": (["Composite"], [""]),
            "https://doi.org/10.3390/biomimetics7020042": (["Composite"], ["SSF"]),
            "https://doi.org/10.3390/biomimetics7030100": ([""], [""]),
            "https://doi.org/10.3390/biomimetics7020078": ([""], [""]),
            "https://doi.org/10.3390/jcs6080237": (["3D"], [""]),
            "https://doi.org/10.3390/biomimetics7020039": ([""], [""]),
            "https://doi.org/10.4067/S0718-221X2022000100435": ([""], [""]),
            "https://doi.org/10.1021/acssuschemeng.2c01314": ([""], [""]),
            "https://doi.org/10.1088/1755-1315/1078/1/012070": ([""], [""]),
            "https://doi.org/10.3390/biomimetics7030129": ([""], [""]),
            "https://doi.org/10.3389/fbuil.2022.965145": ([""], [""]),
            "https://doi.org/10.1007/s10460-022-10366-7": (["Living"], [""]),
            "https://doi.org/10.1007/s44150-022-00073-6": ([""], [""]),
            "https://doi.org/10.1126/sciadv.add7118": (["Electrical"], [""]),
            "https://doi.org/10.1038/s41598-022-24070-3": ([""], [""]),
            "https://doi.org/10.1016/j.funeco.2024.101358": (["Electrical"], [""]),
            "https://doi.org/10.1088/1755-1315/1078/1/012068": ([""], [""]),
            "https://doi.org/10.1016/j.matdes.2022.111530": ([""], [""]),
            "https://doi.org/10.1016/j.mtbio.2023.100545": (["Living"], [""]),
            "https://doi.org/10.1007/s10924-023-02766-5": ([""], [""]),
            "https://doi.org/10.3390/jof9020210": ([""], [""]),
            "https://doi.org/10.1126/sciadv.ade5417": ([""], ["FB"]),
            "https://doi.org/10.3390/ma16062164": ([""], [""]),
            "https://doi.org/10.3390/polym14091738": ([""], [""]),
            "https://doi.org/10.1038/s41598-023-31594-9": ([""], [""]),
            "https://doi.org/10.1186/s40694-023-00155-0": (["Electrical"], [""]),
            "https://doi.org/10.1002/adfm.202301875": (["Living", "Pure"], [""]),
            "https://doi.org/10.3390/ma16093547": ([""], [""]),
            "https://doi.org/10.3390/app13031703": ([""], [""]),
            "https://doi.org/10.1007/s12257-023-0069-5": ([""], [""]),
            "https://doi.org/10.1016/j.xcrp.2023.101424": ([""], [""]),
            "https://doi.org/10.1007/s10924-023-02941-8": ([""], [""]),
            "https://doi.org/10.3390/su15129157": ([""], [""]),
            "https://doi.org/10.1016/j.actbio.2022.04.011": ([""], [""]),
            "https://doi.org/10.3390/biomimetics8020257": (["Living", "3D", "Composite"], [""]),
            "https://doi.org/10.3390/polym15173548": ([""], [""]),
            "https://doi.org/10.1016/j.compositesa.2021.106688": ([""], [""]),
            "https://doi.org/10.3389/fbioe.2023.1229693": ([""], [""]),
            "https://doi.org/10.3390/jof7121018": ([""], [""]),
            "https://doi.org/10.1557/s43580-023-00623-0": ([""], [""]),
            "https://doi.org/10.1016/j.jobab.2023.07.001": ([""], [""]),
            "https://doi.org/10.1038/s41598-023-45842-5": ([""], [""]),
            "https://doi.org/10.1016/j.mimet.2023.106794": ([""], [""]),
            "https://doi.org/10.1002/smll.202302827": ([""], [""]),
            "https://doi.org/10.1038/s41598-019-40442-8": ([""], [""]),
            "https://doi.org/10.1016/j.foodhyd.2023.109289": ([""], [""]),
            "https://doi.org/10.1002/gch2.202300098": ([""], [""]),
            "https://doi.org/10.32604/jrm.2020.09646": ([""], [""]),
            "https://doi.org/10.1051/e3sconf/202343703004": ([""], [""]),
            "https://doi.org/10.1080/12298093.2021.1911401": ([""], [""]),
            "https://doi.org/10.1016/j.aej.2023.10.012": ([""], [""]),
            "https://doi.org/10.1016/j.conbuildmat.2021.124656": ([""], [""]),
            "https://doi.org/10.1038/s41563-022-01429-5": (["Living", "3D"], [""]),
            "https://doi.org/10.1186/s12302-022-00689-x": ([""], [""]),
            "https://doi.org/10.3390/biomimetics8060504": (["3D", "Composite"], [""]),
            "https://doi.org/10.4028/www.scientific.net/AMM.507.415": ([""], [""]),
            "https://doi.org/10.1186/s40694-023-00169-8": ([""], [""]),
            "https://doi.org/10.1016/j.conbuildmat.2023.133346": ([""], [""]),
            "https://doi.org/10.1007/s00339-020-04270-2": ([""], ["FB"]),
            "https://doi.org/10.1016/j.biosystems.2023.105106": (["Living", "Electrical"], [""]),
            "https://doi.org/10.3390/jmmp8010002": ([""], [""]),
            "https://doi.org/10.1002/smll.202309171": ([""], [""]),
            "https://doi.org/10.1038/s41598-023-48203-4": ([""], [""]),
            "https://doi.org/10.1021/acsomega.1c05748": ([""], ["FB"]),
            "https://doi.org/10.1016/j.carbpol.2021.119038": (["Nanopaper"], ["FB"]),
            "https://doi.org/10.3390/ma17020404": ([""], [""]),
            "https://doi.org/10.1007/s42114-021-00271-8": (["Electrical"], [""]),
            "https://doi.org/10.1515/npprj-2019-0045": ([""], [""]),
            "https://doi.org/10.1016/j.carbpol.2017.03.010": ([""], ["FB"]),
            "https://doi.org/10.3390/ma14010136": ([""], [""]),
            "https://doi.org/10.1016/j.btre.2023.e00807": ([""], [""]),
            "https://doi.org/10.1021/acssusresmgt.3c00021": ([""], [""]),
            "https://doi.org/10.1007/s42398-024-00305-z": ([""], [""]),
            "https://doi.org/10.15376/biores.19.2.3421-3435": ([""], [""]),
            "https://doi.org/10.3390/biomimetics9040251": (["3D"], [""]),
            "https://doi.org/10.1002/mame.202300449": ([""], [""]),
            "https://doi.org/10.1016/j.heliyon.2024.e28709": ([""], [""]),
            "https://doi.org/10.1016/j.ijbiomac.2022.04.031": ([""], [""]),
            "https://doi.org/10.1080/12298093.2024.2341492": ([""], [""]),
            "https://doi.org/10.1016/j.mtcomm.2024.109100": ([""], [""]),
            "https://doi.org/10.1017/btd.2024.6": ([""], [""]),
            "https://doi.org/10.1039/d4lf00061g": (["Adhesion"], [""]),
            "https://doi.org/10.3390/biomimetics9060333": ([""], [""]),
            "https://doi.org/10.1038/s41598-024-62561-7": ([""], [""]),
            "https://doi.org/10.1002/gch2.202300315": ([""], [""]),
            "https://doi.org/10.3390/pr12050933": ([""], [""]),
            "https://doi.org/10.3390/biomimetics9070411": (["3D", "Composite"], [""]),
            "https://doi.org/10.1051/e3sconf/202454603003": ([""], [""]),
            "https://doi.org/10.1016/j.conbuildmat.2024.135566": ([""], [""]),
            "https://doi.org/10.3390/pr12081545": ([""], [""]),
            "https://doi.org/10.1186/s40694-024-00178-1": ([""], [""]),
            "https://doi.org/10.1016/j.heliyon.2024.e36263": ([""], [""]),
            "https://doi.org/10.1039/d3va00217a": ([""], [""]),
            "https://doi.org/10.1016/j.clcb.2024.100106": ([""], [""]),
            "https://doi.org/10.3390/designs7010020": ([""], [""]),
            "https://doi.org/10.1039/d3mh01277h": (["Living"], [""]),
            "https://doi.org/10.3390/coatings14070862": ([""], [""]),
            "https://doi.org/10.1016/j.eti.2023.103063": ([""], [""]),
            "https://doi.org/10.1002/advs.202309370": (["Living"], [""]),
            "https://doi.org/10.1007/s10570-024-06067-5": ([""], [""]),
            "https://doi.org/10.1016/j.compositesb.2023.111003": ([""], [""]),
            "https://doi.org/10.1002/advs.202403215": ([""], [""]),
            "https://doi.org/10.1590/1517-7076-RMAT-2024-0193": ([""], [""]),
            "https://doi.org/10.1021/acssuschemeng.3c04795": ([""], [""]),
            "https://doi.org/10.1038/s41598-024-66223-6": (["Electrical"], [""]),
            "https://doi.org/10.1557/s43577-024-00762-1": ([""], [""]),
            "https://doi.org/10.33774/coe-2024-5cc7n": ([""], [""]),
            "https://doi.org/10.1126/scirobotics.adk8019": (["Electrical"], [""]),
            "https://doi.org/10.1017/btd.2024.8": ([""], [""]),
            "https://doi.org/10.1088/1755-1315/1372/1/012066": ([""], [""]),
            "https://doi.org/10.1002/adfm.202412753": ([""], [""]),
            "https://doi.org/10.3390/coatings14040430": (["Living"], [""]),
            "https://doi.org/10.1371/journal.pone.0304614": ([""], ["FB"]),
            "https://doi.org/10.1017/btd.2024.10": (["Living"], [""]),
            "https://doi.org/10.1101/2024.09.28.615565": ([""], [""]),
            "https://doi.org/10.1021/acsabm.4c00586": (["Pure"], [""]),
            "https://doi.org/10.1017/btd.2024.15": ([""], [""]),
            "https://doi.org/10.15575/biodjati.v9i1.30021": ([""], [""]),
            "https://doi.org/10.1016/j.matdes.2018.11.027": ([""], [""]),
            "https://doi.org/10.1038/s41598-018-23171-2": ([""], [""]),
            "https://doi.org/10.1038/s42003-020-1064-4": (["Pure"], ["LSF"]),
            "https://doi.org/10.1038/srep41292": (["Pure"], ["SSF"]),
            "https://doi.org/10.1038/s41598-018-36032-9": ([""], [""]),
            "https://doi.org/10.1002/fam.2637": ([""], [""]),
            "https://doi.org/10.5185/amlett.2018.1977": ([""], [""]),
            "https://doi.org/10.1021/acs.biomac.9b00791": (["Nanopaper"], ["FB"]),
            "https://doi.org/10.1016/j.carbpol.2020.117273": (["Nanopaper"], ["FB"]),
            "https://doi.org/10.1016/j.reactfunctpolym.2019.104428": (["Nanopaper"], ["FB"]),
            "https://doi.org/10.1016/j.compscitech.2020.108327": (["Nanopaper"], ["FB"]),
            "https://doi.org/10.3390/jcs8100412": (["3D", "Composite"], ["SSF"]),
            "https://doi.org/10.1101/2024.05.03.592484": (["Living"], [""]),
            "https://doi.org/10.1017/btd.2024.9": (["3D", "Composite"], ["SSF"]),
            "https://doi.org/10.3390/jcs8100412": (["3D", "Composite"], ["SSF"]),
            "https://doi.org/10.1016/j.carbpol.2024.122800": (["Nanopaper", "Pure"], ["FB"]),
            "https://doi.org/10.1002/sstr.202400130": ([""], [""]),
            "https://doi.org/10.1016/j.bcab.2024.103436": (["Composite"], ["SSF"]),
            "https://doi.org/10.1186/s40694-024-00189-y": (["Composite"], ["SSF"]),
            "https://doi.org/10.3390/biomimetics9110707": (["Composite"], ["SSF"]),
        }

        for doi, (topics, methods) in dois.items():
            try:
                with transaction.atomic():
                    # Import the article data for the given DOI
                    import_success = import_new_article_by_doi(doi)

                    # If import was successful, retrieve the review by DOI
                    if import_success:
                        article = Article.objects.get(doi=doi)

                        # Assign topics to the article
                        for topic_name in topics:
                            if topic_name:  # Ensure topic_name is not empty
                                topic, _ = Topic.objects.get_or_create(name=topic_name)
                                article.topic.add(topic)

                        # Assign methods to the article
                        for method_name in methods:
                            if method_name:  # Ensure method_name is not empty
                                method, _ = Method.objects.get_or_create(name=method_name)
                                article.method.add(method)
                        
                        # Check if "3D" in title or abstract and add the topic "3D"
                        if "3D" in article.title.lower() or "3D" in article.abstract.lower():
                            three_d_topic, _ = Topic.objects.get_or_create(name="3D")
                            article.topic.add(three_d_topic)

                        # Check if "Adhesion" in title or abstract and add the topic "Adhesion"
                        if "Adhesion" in article.title.lower() or "Adhesion" in article.abstract.lower():
                            three_d_topic, _ = Topic.objects.get_or_create(name="Adhesion")
                            article.topic.add(three_d_topic)

                        # Check if "composite" is in the title or "mbc" in abstract and add the topic "Composite"
                        if ("composite" in article.title.lower() or "mbc" in article.abstract.lower()) and "nanopaper" not in article.title.lower() and "nanopaper" not in article.abstract.lower():
                            composite_topic, _ = Topic.objects.get_or_create(name="Composite")
                            article.topic.add(composite_topic)
                            # Also add "SSF" as method
                            ssf_method, _ = Method.objects.get_or_create(name="SSF")
                            article.method.add(ssf_method)

                        # Check if "substrate" and "cellulosic" are in abstract add the method "SSF"
                        if "substrate" in article.abstract.lower() and "cellulosic" in article.abstract.lower():
                            ssf_method, _ = Method.objects.get_or_create(name="SSF")
                            article.method.add(ssf_method)
                        # or "substrate" and "solid" are in abstract add the method "SSF"
                        elif "substrate" in article.abstract.lower() and "solid" in article.abstract.lower():
                            ssf_method, _ = Method.objects.get_or_create(name="SSF")
                            article.method.add(ssf_method)

                        # Check if "liquid" in abstract and add the method "LSF"
                        if "liquid" in article.abstract.lower():
                            lsf_method, _ = Method.objects.get_or_create(name="LSF")
                            article.method.add(lsf_method)

                        # Check if species name is mentioned in the title or abstract
                        # Get all species names using Species model
                        species_list = Species.objects.all()
                        for species in species_list:
                            # Check if any of the species names are mentioned in the title or abstract
                            if species.name.lower() in article.title.lower() or species.name.lower() in article.abstract.lower():
                                # print species name(s) found in the title or abstract
                                print(f"Species {species.name} found in the title or abstract")
                                # If so add a Material with this article and the species name
                                material, created = Material.objects.get_or_create(article=article)
                                material.species.add(species)
                                material.save()                       
        
                        article.save()
                        self.stdout.write(self.style.SUCCESS(f'Successfully imported and updated topics and methods for: {doi}'))
                    else:
                        self.stdout.write(self.style.WARNING(f"The DOI {doi} could not be imported. It might already be present."))

            except Exception as e:
                self.stdout.write(self.style.WARNING(f"Error importing DOI {doi}: {str(e)}"))

        self.stdout.write(self.style.SUCCESS('Article population with topics completed!'))
