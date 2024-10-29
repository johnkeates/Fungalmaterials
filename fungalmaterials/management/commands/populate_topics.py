from django.core.management.base import BaseCommand
from fungalmaterials.models import Topic

class Command(BaseCommand):
	help = 'Populate the Topic model with default data if not already present'
	
    # Topics: Pure, Composite, Nanopaper, 3D, Amadou, Living, Electrical, adhesive

	def handle(self, *args, **kwargs):
		# List of topics to add
		topic_data = [
			{"name": "Pure"},
            {"name": "Composite"},
			{"name": "Nanopaper"},
			{"name": "3D"},
            {"name": "Amadou"},
			{"name": "Living"},
			{"name": "Electrical"},
			{"name": "Adhesion"},
		]

		# Iterate over topic data and check if it exists by name
		for topic in topic_data:
			name = topic["name"]

			# Check if the topic with this name already exists
			if not Topic.objects.filter(name=name).exists():
				# If it doesn't exist, create a new record
				Topic.objects.create(name=name)
				self.stdout.write(self.style.SUCCESS(f'Successfully added: {name}'))
			else:
				# If it exists, just output a message
				self.stdout.write(self.style.WARNING(f'Topic already exists: {name}'))

		self.stdout.write(self.style.SUCCESS('Topic population completed!'))