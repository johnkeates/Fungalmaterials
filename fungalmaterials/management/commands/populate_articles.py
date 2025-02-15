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
        # DOI: (Topics, Methods, Species)
        "https://doi.org/10.1016/j.mtcomm.2024.109784": (["Pure", "Living"], ["LSF"], ["Schizophyllum commune"]),
        "https://doi.org/10.3390/jof8030317": (["Pure"], ["SSF"], ["Fomitella fraxinea", "Ganoderma lucidum", "Ganoderma applanatum", "Bjerkandera adusta", "Microporus affinis", "Trametes versicolor", "Fomitopsis pinicola", "Wolfiporia extensa", "Postia balsamea", "Fomitopsis rosea", "Trametes suaveolens", "Trametes hirsuta"]),
        "https://doi.org/10.3390/biomimetics7020057": (["Composite"], ["SSF"], ["Trametes versicolor"]),
        "https://doi.org/10.3390/jof7121008": (["Pure"], [""], ["Abortiporus biennis", "Bjerkandera adusta", "Trametes gallica", "Trametes trogii", "Daedaleopsis confragosa", "Daedaleopsis tricolor", "Fomes fomentarius", "Fomitiporia mediterranea", "Fomitopsis iberica", "Fomitopsis pinicola", "Ganoderma carnosum", "Ganoderma lucidum", "Irpex lacteus", "Irpiciporus pachyodon", "Trametes betulina", "Neofavolus alveolaris", "Stereum hirsutum", "Terana caerulea", "Trametes hirsuta", "Trametes suaveolens"]),
        "https://doi.org/10.3390/su132111573": (["Composite"], [""], [""]), # LCA
        "https://doi.org/10.3390/biomimetics7020042": (["Composite"], ["SSF"], ["Pleurotus ostreatus"]),
        "https://doi.org/10.3390/biomimetics7030100": (["Composite"], ["SSF"], ["Pleurotus ostreatus"]),
        "https://doi.org/10.3390/biomimetics7020078": (["Composite"], ["SSF"], ["Ganoderma lucidum", "Pycnoporus sanguineus"]),
        "https://doi.org/10.3390/jcs6080237": (["Composite", "3D"], ["SSF"], [""]), # UNDEFINED SPECIES USED GROWKIT
        "https://doi.org/10.3390/biomimetics7020039": (["Composite"], ["SSF"], ["Ganoderma lucidum"]),
        "https://doi.org/10.1021/acssuschemeng.2c01314": (["Composite"], ["SSF"], ["Trametes betulina"]), # LCA
        "https://doi.org/10.1088/1755-1315/1078/1/012070": (["Composite"], ["SSF"], ["Fomes fomentarius"]),
        "https://doi.org/10.3390/biomimetics7030129": ([""], [""], [""]), # STRATEGY ARTICLE
        "https://doi.org/10.3389/fbuil.2022.965145": ([""], [""], [""]), # OR REVIEW?
        "https://doi.org/10.1007/s10460-022-10366-7": (["Living"], [""], [""]), 
        "https://doi.org/10.1007/s44150-022-00073-6": ([""], [""], [""]), # UNDEFINED SPECIES USED GROWKIT
        "https://doi.org/10.1126/sciadv.add7118": (["Electrical"], [""], ["Ganoderma lucidum"]),
        "https://doi.org/10.1038/s41598-022-24070-3": (["Composite"], ["SSF"], ["Pleurotus ostreatus"]),
        "https://doi.org/10.1016/j.funeco.2024.101358": (["Electrical"], ["FB"], ["Agaricus bisporus", "Pleurotus ostreatus", "Hypsizygus tessellatus", "Pleurotus djamor", "Cantharellus cibarius", "Pleurotus eryngii", "Lentinula edodes"]),
        "https://doi.org/10.1088/1755-1315/1078/1/012068": ([""], [""], [""]),
        "https://doi.org/10.1016/j.matdes.2022.111530": (["Composite", "3D"], ["SSF"], ["Pleurotus ostreatus"]),
        "https://doi.org/10.1016/j.mtbio.2023.100545": (["Living"], ["LSF"], ["Aspergillus niger"]),
        "https://doi.org/10.1007/s10924-023-02766-5": (["Pure"], ["LSF"], ["Aspergillus niger", "Mucor hiemalis", "Penicillium nalgiovense"]),
        "https://doi.org/10.3390/jof9020210": (["Composite"], ["SSF"], [""]), # A LOT OF SPECIES 75!
        "https://doi.org/10.1126/sciadv.ade5417": ([""], ["FB"], ["Fomes fomentarius"]),
        "https://doi.org/10.3390/ma16062164": (["Composite"], ["SSF"], [""]),
        "https://doi.org/10.3390/polym14091738": (["Composite"], ["LSF"], ["Aspergillus oryzae"]),
        "https://doi.org/10.1038/s41598-023-31594-9": (["Composite"], ["SSF"], ["Pleurotus ostreatus"]),
        "https://doi.org/10.1186/s40694-023-00155-0": (["Electrical"], ["SSF"], ["Pleurotus ostreatus", "Hericium erinaceus"]),
        "https://doi.org/10.1002/adfm.202301875": (["Living", "Pure"], ["LSF"], ["Ganoderma lucidum"]),
        "https://doi.org/10.3390/ma16093547": (["Composite"], ["SSF"], ["Trametes versicolor", "Pleurotus ostreatus", "Pleurotus eryngii", "Ganoderma carnosum", "Fomitopsis pinicola"]),
        "https://doi.org/10.3390/app13031703": ([""], [""], [""]), # MODELLING
        "https://doi.org/10.1007/s12257-023-0069-5": (["Pure"], ["SSF"], ["Trametes orientalis"]),
        "https://doi.org/10.1016/j.xcrp.2023.101424": (["Composite"], ["SSF"], ["Pleurotus eryngii"]),
        "https://doi.org/10.1007/s10924-023-02941-8": (["Pure"], [""], ["Penicillium camemberti"]),
        "https://doi.org/10.3390/su15129157": (["Composite"], ["SSF"], ["Pleurotus ostreatus"]),
        "https://doi.org/10.1016/j.actbio.2022.04.011": ([""], ["FB"], ["Agaricus bisporus", "Grifola frondosa", "Ganoderma lingzhi"]),
        "https://doi.org/10.3390/biomimetics8020257": (["Living", "3D", "Composite"], [""], [""]),
        "https://doi.org/10.3390/polym15173548": ([""], [""], ["Heterobasidion annosum", "Phanerochaete chrysosporium", "Pleurotus ostreatus", "Trametes versicolor", "Lentinus lepideus"]),
        "https://doi.org/10.1016/j.compositesa.2021.106688": (["Composite"], ["SSF"], ["Pleurotus ostreatus", "Trametes hirsuta"]),
        "https://doi.org/10.3389/fbioe.2023.1229693": (["Composite"], ["SSF"], ["Ganoderma lucidum"]),
        "https://doi.org/10.3390/jof7121018": ([""], [""], ["Aspergillus nidulans"]),
        "https://doi.org/10.1557/s43580-023-00623-0": (["Composite"], ["SSF"], ["Pleurotus ostreatus"]),
        "https://doi.org/10.1016/j.jobab.2023.07.001": ([""], [""], ["Pleurotus ostreatus"]),
        "https://doi.org/10.1038/s41598-023-45842-5": ([""], [""], [""]), # UNDEFINED SPECIES MATERIAL FROM ECOVATIVE
        "https://doi.org/10.1016/j.mimet.2023.106794": ([""], [""], ["Flammulina velutipes", "Ganoderma lucidum", "Hericium erinaceus", "Hypsizygus ulmarius", "Pleurotus cornucopiae", "Pleurotus ostreatus", "Pleurotus pulmonarius", "Trametes hirsuta", "Trametes versicolor"]),
        "https://doi.org/10.1002/smll.202302827": (["Composite"], ["SSF"], [""]),
        "https://doi.org/10.1038/s41598-019-40442-8": ([""], [""], [""]), # UNDEFINED SPECIES MATERIAL FROM ECOVATIVE
        "https://doi.org/10.1016/j.foodhyd.2023.109289": ([""], [""], ["Ganoderma lucidum", "Auricularia polytricha", "Pleurotus ostreatus"]),
        "https://doi.org/10.1002/gch2.202300098": ([""], [""], ["Rhizopus delemar"]),
        "https://doi.org/10.32604/jrm.2020.09646": (["Composite"], ["SSF"], [""]),  # UNDEFINED SPECIES MATERIAL FROM ECOVATIVE
        "https://doi.org/10.1051/e3sconf/202343703004": ([""], [""], ["Pleurotus djamor"]),
        "https://doi.org/10.1080/12298093.2021.1911401": ([""], [""], ["Trametes versicolor", "Pycnoporus coccineus", "Ganoderma lucidum"]), # AND MORE SPECIES!
        "https://doi.org/10.1016/j.conbuildmat.2021.124656": ([""], [""], ["Pleurotus ostreatus"]), # AND TWO OTHER UNKNOWN SPECIES
        "https://doi.org/10.1038/s41563-022-01429-5": (["Living", "3D"], [""], ["Ganoderma lucidum"]),
        "https://doi.org/10.1186/s12302-022-00689-x": ([""], [""], [""]), # LCA
        "https://doi.org/10.3390/biomimetics8060504": (["3D", "Composite"], [""], ["Pleurotus ostreatus"]),
        "https://doi.org/10.4028/www.scientific.net/AMM.507.415": ([""], [""], [""]), # DOI NOT WORKING
        "https://doi.org/10.1186/s40694-023-00169-8": (["Composite"], ["SSF"], ["Fomes fomentarius"]),
        "https://doi.org/10.1016/j.conbuildmat.2023.133346": ([""], [""], ["Fomitopsis pinicola", "Agaricus bisporus"]),
        "https://doi.org/10.1007/s00339-020-04270-2": ([""], ["FB"], ["Fomes fomentarius"]),
        "https://doi.org/10.1016/j.biosystems.2023.105106": (["Living", "Electrical"], ["LSF"], ["Ganoderma sessile"]),
        "https://doi.org/10.3390/jmmp8010002": (["3D", "Composite"], ["SSF"], [""]), # UNDEFINED SPECIES USED GROWKIT
        "https://doi.org/10.1002/smll.202309171": ([""], [""], ["Phanerochaete chrysosporium", "Pleurotus ostreatus", "Trametes versicolor", "Fomes fomentarius"]),
        "https://doi.org/10.1038/s41598-023-48203-4": ([""], [""], ["Ganoderma lucidum", "Ganoderma sessile"]),
        "https://doi.org/10.1021/acsomega.1c05748": ([""], ["FB"], ["Fomes fomentarius"]),
        "https://doi.org/10.1016/j.carbpol.2021.119038": (["Nanopaper"], ["FB"], ["Lentinula edodes", "Pleurotus ostreatus", "Flammulina velutipes"]),
        "https://doi.org/10.3390/ma17020404": (["Composite"], ["SSF"], ["Ganoderma lucidum", "Trametes versicolor"]),
        "https://doi.org/10.1007/s42114-021-00271-8": (["Electrical"], [""], ["Ganoderma lucidum"]),
        "https://doi.org/10.1515/npprj-2019-0045": ([""], [""], ["Ganoderma lucidum"]),
        "https://doi.org/10.1016/j.carbpol.2017.03.010": ([""], ["FB"], ["Agaricus bisporus"]),
        "https://doi.org/10.3390/ma14010136": (["Composite"], ["SSF"], ["Ganoderma applanatum"]),
        "https://doi.org/10.1016/j.btre.2023.e00807": ([""], [""], ["Pleurotus ostreatus", "Trametes elegans"]),
        "https://doi.org/10.1021/acssusresmgt.3c00021": ([""], [""], ["Rhizopus delemar"]),
        "https://doi.org/10.15376/biores.19.2.3421-3435": (["Composite"], ["SSF"], ["Ganoderma lucidum"]),
        "https://doi.org/10.3390/biomimetics9040251": (["3D"], [""], [""]), # UNDEFINED SPECIES USED GROWKIT
        "https://doi.org/10.1002/mame.202300449": (["Composite"], ["SSF"], ["Pleurotus ostreatus"]),
        "https://doi.org/10.1016/j.heliyon.2024.e28709": ([""], ["LSF"], ["Abortiporus biennis", "Fomitopsis iberica", "Stereum hirsutum"]),
        "https://doi.org/10.1016/j.ijbiomac.2022.04.031": ([""], [""], ["Rhizopus delemar"]),
        "https://doi.org/10.1080/12298093.2024.2341492": (["Composite"], ["SSF"], ["Ganoderma lucidum", "Pleurotus ostreatus", "Trametes versicolor"]),
        "https://doi.org/10.1016/j.mtcomm.2024.109100": (["Pure"], ["LSF", "SSF"], ["Fomes fomentarius", "Pleurotus eryngii", "Trametes versicolor", "Fomitopsis pinicola"]),
        "https://doi.org/10.1017/btd.2024.6": (["Pure"], ["SSF"], ["Ganoderma lucidum", "Pleurotus djamor"]),
        "https://doi.org/10.1039/d4lf00061g": (["Adhesion"], [""], ["Trametes versicolor"]),
        "https://doi.org/10.3390/biomimetics9060333": ([""], [""], [""]), # SURVEY
        "https://doi.org/10.1038/s41598-024-62561-7": ([""], [""], [""]), # LCA
        "https://doi.org/10.1002/gch2.202300315": (["Electrical"], [""], ["Agaricus bisporus", "Pleurotus eryngii"]),
        "https://doi.org/10.3390/pr12050933": (["Pure"], [""], [""]), # USED MATERIAL FROM MOGU
        "https://doi.org/10.3390/biomimetics9070411": (["3D", "Composite"], [""], [""]), # UNDEFINED SPECIES USED GROWKIT
        "https://doi.org/10.1051/e3sconf/202454603003": (["Composite"], ["SSF"], ["Pleurotus pulmonarius", "Pleurotus ostreatus"]),
        "https://doi.org/10.1016/j.conbuildmat.2024.135566": (["Composite"], ["SSF"], ["Trametes hirsuta"]),
        "https://doi.org/10.3390/pr12081545": ([""], [""], ["Fomes fomentarius"]),
        "https://doi.org/10.1186/s40694-024-00178-1": ([""], [""], ["Rhizopus delemar"]),
        "https://doi.org/10.1016/j.heliyon.2024.e36263": (["Pure"], ["LSF"], ["Schizophyllum commune"]),
        "https://doi.org/10.1039/d3va00217a": ([""], ["LSF"], ["Thermomyces lanuginosus", "Purpureocillium lilacinum"]),
        "https://doi.org/10.1016/j.clcb.2024.100106": ([""], [""], [""]), # LCA
        "https://doi.org/10.3390/designs7010020": ([""], [""], [""]), # UNDEFINED SPECIES USED GROWKIT
        "https://doi.org/10.1039/d3mh01277h": (["Living", "3D"], ["SSF"], ["Ganoderma lucidum"]),
        "https://doi.org/10.3390/coatings14070862": (["Composite"], ["SSF"], ["Auricularia auricula-judae", "Schizophyllum commune", "Pleurotus ostreatus", "Pleurotus sajor-caju"]),
        "https://doi.org/10.1016/j.eti.2023.103063": (["Composite"], ["SSF"], ["Trametes versicolor", "Trametes pubescens"]),
        "https://doi.org/10.1002/advs.202309370": (["Living", "Composite"], ["SSF"], ["Ganoderma lucidum"]),
        "https://doi.org/10.1007/s10570-024-06067-5": ([""], [""], ["Irpex lacteus", "Fomes fomentarius", "Trametes versicolor", "Ganoderma lucidum", "Fomitopsis pinicola", "Pleurotus ostreatus", "Schizophyllum commune"]),
        "https://doi.org/10.1016/j.compositesb.2023.111003": (["Composite"], ["SSF"], ["Trametes versicolor"]),
        "https://doi.org/10.1002/advs.202403215": (["Composite"], ["SSF"], ["Armillaria tabescens"]),
        "https://doi.org/10.1590/1517-7076-RMAT-2024-0193": (["Composite"], ["SSF"], ["Pleurotus ostreatus"]),
        "https://doi.org/10.1021/acssuschemeng.3c04795": ([""], ["FB"], ["Flammulina velutipes", "Ganoderma lucidum"]),
        "https://doi.org/10.1038/s41598-024-66223-6": (["Electrical"], [""], [""]),
        "https://doi.org/10.1557/s43577-024-00762-1": ([""], ["SSF"], ["Ganoderma lucidum", "Pleurotus eryngii"]),
        "https://doi.org/10.33774/coe-2024-5cc7n": (["Composite"], ["SSF"], ["Pleurotus ostreatus"]),
        "https://doi.org/10.1126/scirobotics.adk8019": (["Electrical"], [""], [""]),
        "https://doi.org/10.1017/btd.2024.8": (["Composite"], ["SSF"], ["Ganoderma lucidum", "Pleurotus ostreatus"]),
        "https://doi.org/10.1088/1755-1315/1372/1/012066": (["Composite", "Electrical"], ["SSF"], ["Pleurotus ostreatus"]),
        "https://doi.org/10.1002/adfm.202412753": (["Pure", "Nanopaper"], ["FB"], ["Agaricus bisporus", "Hericium erinaceus"]),
        "https://doi.org/10.3390/coatings14040430": (["Living"], [""], ["Aspergillus niger", "Aspergillus versicolor", "Aureobasidium melanogenum", "Aureobasidium pullulans", "Penicillium crustosum"]),
        "https://doi.org/10.1371/journal.pone.0304614": ([""], ["FB"], ["Fomes fomentarius"]),
        "https://doi.org/10.1017/btd.2024.10": (["Living"], [""], [""]),
        "https://doi.org/10.1101/2024.09.28.615565": (["Pure"], ["LSF"], ["Aspergillus nidulans"]),
        "https://doi.org/10.1021/acsabm.4c00586": (["Pure"], [""], ["Ganoderma sessile"]), # USED MYLO MATERIAL PRODUCED BY BOLT THREAD
        "https://doi.org/10.1017/btd.2024.15": (["Living", "Composite"], ["SSF"], ["Ganoderma lucidum"]),
        "https://doi.org/10.15575/biodjati.v9i1.30021": ([""], [""], [""]),
        "https://doi.org/10.1016/j.matdes.2018.11.027": (["Composite"], ["SSF"], ["Trametes multicolor", "Pleurotus ostreatus"]),
        "https://doi.org/10.1038/s41598-018-23171-2": (["Pure"], ["LSF"], ["Schizophyllum commune"]),
        "https://doi.org/10.1038/s42003-020-1064-4": (["Pure"], ["LSF"], ["Schizophyllum commune"]),
        "https://doi.org/10.1038/srep41292": (["Pure"], ["SSF"], ["Ganoderma lucidum", "Pleurotus ostreatus"]),
        "https://doi.org/10.1038/s41598-018-36032-9": (["Composite"], ["SSF"], ["Trametes versicolor"]),
        "https://doi.org/10.1002/fam.2637": (["Composite"], [""], [""]),
        "https://doi.org/10.5185/amlett.2018.1977": ([""], [""], [""]),
        "https://doi.org/10.1021/acs.biomac.9b00791": (["Nanopaper"], ["FB"], [""]),
        "https://doi.org/10.1016/j.carbpol.2020.117273": (["Nanopaper"], ["FB"], [""]),
        "https://doi.org/10.1016/j.reactfunctpolym.2019.104428": (["Nanopaper"], ["FB"], [""]),
        "https://doi.org/10.1016/j.compscitech.2020.108327": (["Nanopaper"], ["FB"], [""]),
        "https://doi.org/10.3390/jcs8100412": (["3D", "Composite"], ["SSF"], [""]),
        "https://doi.org/10.1101/2024.05.03.592484": (["Living"], [""], [""]),
        "https://doi.org/10.1017/btd.2024.9": (["3D", "Composite"], ["SSF"], [""]),
        "https://doi.org/10.3390/jcs8100412": (["3D", "Composite"], ["SSF"], ["Trametes versicolor"]),
        "https://doi.org/10.1016/j.carbpol.2024.122800": (["Nanopaper", "Pure"], ["FB"], ["Pleurotus ostreatus", "Agaricus bisporus"]),
        "https://doi.org/10.1002/sstr.202400130": (["Pure"], [""], ["Saccharomyces cerevisiae"]),
        "https://doi.org/10.1016/j.bcab.2024.103436": (["Composite"], ["SSF"], [""]),
        "https://doi.org/10.1186/s40694-024-00189-y": (["Composite"], ["SSF"], ["Ganoderma sessile", "Pleurotus pulmonarius", "Trametes versicolor"]),
        "https://doi.org/10.3390/biomimetics9110707": (["Composite"], ["SSF"], ["Ganoderma lucidum"]),
        "https://doi.org/10.1021/acsomega.4c07661": (["Pure"], ["LSF"], ["Fomes fomentarius"]),
        "https://doi.org/10.1038/s41598-024-77435-1": (["Composite"], ["SSF"], ["Pleurotus sajor-caju"]),
        "https://doi.org/10.3390/ma17246050": (["Composite"], ["SSF"], ["Daedaleopsis tricolor", "Stereum hirsutum", "Fomes fomentarius", "Trametes versicolor", "Ganoderma luciducm", "Ganoderma applanatum", "Bjerkandera adusta", "Hericium erinaceus", "Phellinus nigricans"]),
        "https://doi.org/10.1017/btd.2024.26": (["Composite"], ["SSF"], ["Pleurotus ostreatus"]),
        "https://doi.org/10.3390/ma17246111": (["Composite"], ["SSF"], ["Trametes versicolor"]),
        "https://doi.org/10.1016/j.cej.2024.158382": (["Composite"], ["SSF"], ["Ganoderma lucidum"]),
        "https://doi.org/10.1002/adfm.202412196": (["Pure"], ["SSF"], ["Ganoderma lucidum"]),
        "https://doi.org/10.1177/17442591241300711": (["Composite"], ["SSF"], ["Pleurotus ostreatus", "Trametes versicolor"]),
    }

        for doi, (topics, methods, species_names) in dois.items():
            try:
                with transaction.atomic():
                    # Import the article data for the given DOI
                    import_success = import_new_article_by_doi(doi)

                    # If import was successful, retrieve the article by DOI
                    if import_success:
                        article = Article.objects.get(doi=doi)

                        # Retrieve all materials associated with the article
                        materials = Material.objects.filter(article=article)

                        # List of hardcoded species
                        hardcoded_species = []
                        for species_name in species_names:
                            hardcoded_species.append(species_name)
                        # print(F"Hardcoded species: {hardcoded_species}")

                        # List of species in the article
                        present_species = []
                        for material in materials:
                            for species in material.species.all():
                                present_species.append(species.name)
                        # print(F"Present species: {present_species}")

                        # Create new material for each hardcoded species not present in the article
                        for species_name in hardcoded_species:
                            if species_name and species_name not in present_species:
                                species, _ = Species.objects.get_or_create(name=species_name)
                                print(f"Species {species_name} found and added as material")
                                new_material = Material.objects.create(article=article)
                                new_material.species.add(species)
                                new_material.save()

                        # Retrieve all materials associated with the article again after adding new materials
                        materials = Material.objects.filter(article=article)

                        # If no materials exist, create a virtual material to hold all topics and methods
                        if not materials.exists():
                            material = Material.objects.create(article=article)
                            materials = [material]

                        # Assign topics and methods to each material
                        for material in materials:
                            # Assign topics to the material
                            for topic_name in topics:
                                if topic_name:  # Skip empty names
                                    topic, _ = Topic.objects.get_or_create(name=topic_name)
                                    material.topic.add(topic)

                            # Assign methods to the material
                            for method_name in methods:
                                if method_name:
                                    method, _ = Method.objects.get_or_create(name=method_name)
                                    material.method.add(method)

                        # Check if "3D" in title or abstract and add the topic "3D"
                        if "3D" in article.title.lower() or "3D" in article.abstract.lower():
                            three_d_topic, _ = Topic.objects.get_or_create(name="3D")
                            material.topic.add(three_d_topic)

                        # Check if "Adhesion" in title or abstract and add the topic "Adhesion"
                        if "Adhesion" in article.title.lower() or "Adhesion" in article.abstract.lower():
                            three_d_topic, _ = Topic.objects.get_or_create(name="Adhesion")
                            material.topic.add(three_d_topic)

                        # Check if "composite" is in the title or "mbc" in abstract and add the topic "Composite"
                        if ("composite" in article.title.lower() or "mbc" in article.abstract.lower()) and "nanopaper" not in article.title.lower() and "nanopaper" not in article.abstract.lower():
                            composite_topic, _ = Topic.objects.get_or_create(name="Composite")
                            material.topic.add(composite_topic)
                            # Also add "SSF" as method
                            ssf_method, _ = Method.objects.get_or_create(name="SSF")
                            material.method.add(ssf_method)

                        # Check if "substrate" and "cellulosic" are in abstract add the method "SSF"
                        if "substrate" in article.abstract.lower() and "cellulosic" in article.abstract.lower():
                            ssf_method, _ = Method.objects.get_or_create(name="SSF")
                            material.method.add(ssf_method)
                        # or "substrate" and "solid" are in abstract add the method "SSF"
                        elif "substrate" in article.abstract.lower() and "solid" in article.abstract.lower():
                            ssf_method, _ = Method.objects.get_or_create(name="SSF")
                            material.method.add(ssf_method)

                        # Check if "liquid" in abstract and add the method "LSF"
                        if "liquid" in article.abstract.lower():
                            lsf_method, _ = Method.objects.get_or_create(name="LSF")
                            material.method.add(lsf_method)

                        # Save changes to the material and article
                        article.save()
                        material.save()

                        self.stdout.write(self.style.SUCCESS(f'Successfully imported and updated topics and methods for: {doi}'))
                    else:
                        self.stdout.write(self.style.WARNING(f"The DOI {doi} could not be imported. It might already be present."))

            except Exception as e:
                self.stdout.write(self.style.WARNING(f"Error importing DOI {doi}: {str(e)}"))

        self.stdout.write(self.style.SUCCESS('Article population with topics completed!'))
