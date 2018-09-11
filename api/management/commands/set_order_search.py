from django.core.management.base import BaseCommand, CommandError
from api.models import *

class Command(BaseCommand):
	help = 'Updates the search field for all orders'

	def handle(self, *args, **options):
		for order in Order.objects.with_documents().all():
			order.search = order.document
			order.save(update_fields=['search'])
			self.stdout.write("Updated orders to have search fields")

		self.stdout.write(self.style.SUCCESS('Successfully updated all order search fields'))