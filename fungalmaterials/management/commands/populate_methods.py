from django.core.management.base import BaseCommand
from fungalmaterials.models import Method

class Command(BaseCommand):
	help = 'Populate the Method model with default data if not already present'
	
    # Methods: LSF, SSF, FB

	def handle(self, *args, **kwargs):
		# List of methods to add
		method_data = [
			{"name": "LSF"},
            {"name": "SSF"},
			{"name": "FB"},
		]

		# Iterate over method data and check if it exists by name
		for method in method_data:
			name = method["name"]

			# Check if the method with this name already exists
			if not Method.objects.filter(name=name).exists():
				# If it doesn't exist, create a new record
				Method.objects.create(name=name)
				self.stdout.write(self.style.SUCCESS(f'Successfully added: {name}'))
			else:
				# If it exists, just output a message
				self.stdout.write(self.style.WARNING(f'Method already exists: {name}'))

		self.stdout.write(self.style.SUCCESS('Method population completed!'))