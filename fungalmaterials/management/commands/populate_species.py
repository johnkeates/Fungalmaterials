from django.core.management.base import BaseCommand
from fungalmaterials.models import Species

class Command(BaseCommand):
	help = 'Populate the Species model with default data if not already present'
	
	# Phyla: Basidiomycota, Ascomycota, Blastocladiomycota, Mycoromycota, Opisthosporidia

	def handle(self, *args, **kwargs):
		# List of species to add
		species_data = [
			{"name": "Abortiporus biennis", "phylum": "Basidiomycota"},
			{"name": "Agaricus bisporus", "phylum": "Basidiomycota"},
			{"name": "Agrocybe aegerita", "phylum": "Basidiomycota"},
			{"name": "Allomyces arbusculus", "phylum": "Blastocladiomycota"},
			{"name": "Bjerkandera adusta", "phylum": "Basidiomycota"},
			{"name": "Botrytis cinerea", "phylum": "Ascomycota"},
			{"name": "Ceriporia lacerata", "phylum": "Basidiomycota"},
			{"name": "Coprinellus micaceus", "phylum": "Basidiomycota"},
			{"name": "Coprinopsis cinerea", "phylum": "Basidiomycota"},
			{"name": "Daedaleopsis confragosa", "phylum": "Basidiomycota"},
			{"name": "Daedaleopsis tricolor", "phylum": "Basidiomycota"},
			{"name": "Flammulina velutipes", "phylum": "Basidiomycota"},
			{"name": "Fomes fomentarius", "phylum": "Basidiomycota"},
			{"name": "Fomes inzengae", "phylum": "Basidiomycota"},
			{"name": "Fomitiporia mediterranea", "phylum": "Basidiomycota"},
			{"name": "Fomitopsis iberica", "phylum": "Basidiomycota"},
			{"name": "Fomitopsis pinicola", "phylum": "Basidiomycota"},
			{"name": "Fusarium graminearum", "phylum": "Ascomycota"},
			{"name": "Fusarium oxysporum", "phylum": "Ascomycota"},
			{"name": "Ganoderma applanatum", "phylum": "Basidiomycota"},
			{"name": "Ganoderma carnosum", "phylum": "Basidiomycota"},
			{"name": "Ganoderma curtisii", "phylum": "Basidiomycota"},
			{"name": "Ganoderma lucidum", "phylum": "Basidiomycota"},
			{"name": "Ganoderma mexicanum", "phylum": "Basidiomycota"},
			{"name": "Ganoderma resinaceum", "phylum": "Basidiomycota"},
			{"name": "Ganoderma sessile", "phylum": "Basidiomycota"},
			{"name": "Gloeophyllum odoratum", "phylum": "Basidiomycota"},
			{"name": "Gloeophyllum sepiarium", "phylum": "Basidiomycota"},
			{"name": "Grifola frondosa", "phylum": "Basidiomycota"},
			{"name": "Hypsizygus marmoreus", "phylum": "Basidiomycota"},
			{"name": "Hypsizygus ulmarius", "phylum": "Basidiomycota"},
			{"name": "Irpex lacteus", "phylum": "Basidiomycota"},
			{"name": "Irpiciporus pachyodon", "phylum": "Basidiomycota"},
			{"name": "Kuehneromyces mutabilis", "phylum": "Basidiomycota"},
			{"name": "Laetiporus sulphureus", "phylum": "Basidiomycota"},
			{"name": "Lentinula edodes", "phylum": "Basidiomycota"},
			{"name": "Lentinus crinitus", "phylum": "Basidiomycota"},
			{"name": "Lentinus velutinus", "phylum": "Basidiomycota"},
			{"name": "Lichtheimia corymbifera", "phylum": "Mycoromycota"},
			{"name": "Megasporoporia minor", "phylum": "Basidiomycota"},
			{"name": "Mucor genevensis", "phylum": "Mycoromycota"},
			{"name": "Mucor mucedo", "phylum": "Mycoromycota"},
			{"name": "Neofavolus alveolares", "phylum": "Basidiomycota"},
			{"name": "Oxyporus latemarginatus", "phylum": "Basidiomycota"},
			{"name": "Panus conchatus", "phylum": "Basidiomycota"},
			{"name": "Phaeolus schweinitzii", "phylum": "Basidiomycota"},
			{"name": "Phellinus ellipsoideus", "phylum": "Basidiomycota"},
			{"name": "Phycomyces blakesleeanus", "phylum": "Mycoromycota"},
			{"name": "Phytophthora cinnamomi", "phylum": "Opisthosporidia"},
			{"name": "Piptoporus betulinus", "phylum": "Basidiomycota"},
			{"name": "Pleurotus albidus", "phylum": "Basidiomycota"},
			{"name": "Pleurotus citrinopileatus", "phylum": "Basidiomycota"},
			{"name": "Pleurotus cornucopiae", "phylum": "Basidiomycota"},
			{"name": "Pleurotus djamor", "phylum": "Basidiomycota"},
			{"name": "Pleurotus eryngii", "phylum": "Basidiomycota"},
			{"name": "Pleurotus ostreatus", "phylum": "Basidiomycota"},
			{"name": "Pleurotus pulmonarius", "phylum": "Basidiomycota"},
			{"name": "Pleurotus salmoneostramineus", "phylum": "Basidiomycota"},
			{"name": "Polyporus arcularius", "phylum": "Basidiomycota"},
			{"name": "Polyporus brumalis", "phylum": "Basidiomycota"},
			{"name": "Pycnoporus sanguineus", "phylum": "Basidiomycota"},
			{"name": "Rhizomucor miehei", "phylum": "Mycoromycota"},
			{"name": "Rhizopus oryzae", "phylum": "Mycoromycota"},
			{"name": "Saksenaea vasiformis", "phylum": "Mycoromycota"},
			{"name": "Schizophyllum commune", "phylum": "Basidiomycota"},
			{"name": "Stereum hirsutum", "phylum": "Basidiomycota"},
			{"name": "Stropharia rugosoannulata", "phylum": "Basidiomycota"},
			{"name": "Terana caerulea", "phylum": "Basidiomycota"},
			{"name": "Trametes betulina", "phylum": "Basidiomycota"},
			{"name": "Trametes gallica", "phylum": "Basidiomycota"},
			{"name": "Trametes hirsuta", "phylum": "Basidiomycota"},
			{"name": "Trametes multicolor", "phylum": "Basidiomycota"},
			{"name": "Trametes pubescens", "phylum": "Basidiomycota"},
			{"name": "Trametes suaveolens", "phylum": "Basidiomycota"},
			{"name": "Trametes trogii", "phylum": "Basidiomycota"},
			{"name": "Trametes versicolor", "phylum": "Basidiomycota"},
			{"name": "Trichaptum abietinum", "phylum": "Basidiomycota"},
			{"name": "Trichoderma asperellum", "phylum": "Ascomycota"},
			{"name": "Tricholoma terreum", "phylum": "Basidiomycota"},
			{"name": "Xylaria hypoxylon", "phylum": "Ascomycota"},
		]

		# Iterate over species data and check if it exists by name
		for species in species_data:
			name = species["name"]
			phylum = species["phylum"]

			# Check if the species with this name already exists
			if not Species.objects.filter(name=name).exists():
				# If it doesn't exist, create a new record
				Species.objects.create(name=name, phylum=phylum)
				self.stdout.write(self.style.SUCCESS(f'Successfully added: {name}'))
			else:
				# If it exists, just output a message
				self.stdout.write(self.style.WARNING(f'Species already exists: {name}'))

		self.stdout.write(self.style.SUCCESS('Species population completed!'))