from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.search import SearchVectorField, SearchVector
from django.utils import timezone

# Create your models here.
class Team(models.Model):
	name = models.CharField(max_length=50, unique=True)
	shopify_access_token = models.TextField(null=True)
	shopify_store_name = models.CharField(max_length=50, null=True)


class UserProfile(models.Model):
	USERTYPES = (
		('a', 'admin'),
		('w', 'worker'),
	)

	user = models.OneToOneField(User, on_delete=models.CASCADE)
	team = models.ForeignKey(Team, related_name='userprofiles', on_delete=models.CASCADE, null=True)
	account_type = models.CharField(max_length=1, choices=USERTYPES, default='a')
	email = models.TextField(null=True)

	def get_username_display(self):
		username_pieces = self.user.username.rsplit('_', 1)
		return username_pieces[0]

class Product(models.Model):
	PRODUCT_TYPES = (
		('rm', 'raw materials'),
		('fg', 'finished goods'),
	)
	team = models.ForeignKey(Team, related_name='products', on_delete=models.CASCADE)
	name = models.CharField(max_length=50)
	# code = models.CharField(max_length=20)
	category = models.CharField(max_length=2, choices=PRODUCT_TYPES, default='rm')
	icon = models.CharField(max_length=50)
	created_at = models.DateTimeField(default=timezone.now, blank=True)
	unit = models.CharField(max_length=20, default="kilogram")
	is_trashed = models.BooleanField(default=False, db_index=True)

class ShopifySKU(models.Model):
	team = models.ForeignKey(Team, related_name='shopify_skus', on_delete=models.CASCADE)
	name = models.CharField(max_length=300)
	variant_id = models.CharField(max_length=50, unique=True)
	variant_sku = models.CharField(max_length=100, null=True)
	product = models.ForeignKey(Product, related_name='shopify_skus', on_delete=models.CASCADE, null=True)
	conversion_factor = models.DecimalField(default=1, max_digits=10, decimal_places=6)
	# CHANGE ShopifySKU to ExternalSKU and also include a row with the channel e.g. shopify


class Recipe(models.Model):
	product = models.ForeignKey(Product, related_name='recipes', on_delete=models.CASCADE)
	default_batch_size = models.DecimalField(default=1, max_digits=10, decimal_places=3)
	is_trashed = models.BooleanField(default=False, db_index=True)
	created_at = models.DateTimeField(default=timezone.now, blank=True)

class Ingredient(models.Model):
	recipe = models.ForeignKey(Recipe, related_name="ingredients", on_delete=models.CASCADE)
	product = models.ForeignKey(Product, related_name="ingredients", on_delete=models.CASCADE)
	amount = models.DecimalField(default=1, max_digits=10, decimal_places=3)
	is_trashed = models.BooleanField(default=False, db_index=True)

class Batch(models.Model):
	STATUSES = (
		('i', 'in progress'),
		('c', 'completed')
	)
	status = models.CharField(max_length=1, choices=STATUSES, default='i')
	started_at = models.DateTimeField(default=timezone.now, blank=True)
	completed_at = models.DateTimeField(blank=True, null=True)
	product = models.ForeignKey(Product, related_name="batches", on_delete=models.CASCADE)
	active_recipe = models.ForeignKey(Recipe, related_name="batches", on_delete=models.CASCADE, null=True)
	amount = models.DecimalField(default=1, max_digits=10, decimal_places=3)
	is_trashed = models.BooleanField(default=False, db_index=True)
	calendar_start = models.DateTimeField(blank=True, null=True)
	calendar_end = models.DateTimeField(blank=True, null=True)


# can you receive negative inventory??
class ReceivedInventory(models.Model):
	product = models.ForeignKey(Product, related_name='received_inventory', on_delete=models.CASCADE)
	amount = models.DecimalField(default=1, max_digits=10, decimal_places=3)
	received_at = models.DateTimeField(default=timezone.now, blank=True)
	is_trashed = models.BooleanField(default=False, db_index=True)
	dollar_value = models.DecimalField(max_digits=10, decimal_places=2, null=True)
	message = models.CharField(max_length=200, blank=True, default="Received Inventory")

class OrderManager(models.Manager):
	def with_documents(self):
		vector = SearchVector('name') + \
		SearchVector('channel')
		return self.get_queryset().annotate(document=vector)

class Order(models.Model):
	team = models.ForeignKey(Team, related_name='orders', on_delete=models.CASCADE)
	STATUSES = (
		('i', 'in progress'),
		('c', 'completed'),
		('x', 'cancelled')
	)
	status = models.CharField(max_length=1, choices=STATUSES, default='i')
	name = models.CharField(max_length=300, blank=True)
	number = models.IntegerField(null=True, db_index=True)
	channel = models.CharField(max_length=20, default='manual')
	created_at = models.DateTimeField(blank=True, null=True)
	# change created at to placed on
	due_date = models.DateTimeField(blank=True, null=True)
	url = models.CharField(max_length=200, blank=True, null=True)
	customer = models.CharField(max_length=150, blank=True, null=True)
	# add in customer name
	keywords = models.CharField(max_length=200, blank=True)
	search = SearchVectorField(null=True)

	objects = OrderManager()

	def save(self, *args, **kwargs):
		self.refreshKeywords()
		super(Order, self).save(*args, **kwargs)
		if 'update_fields' not in kwargs or 'search' not in kwargs['update_fields']:
			instance = self._meta.default_manager.with_documents().filter(pk=self.pk)[0]
			instance.search = instance.document
			instance.save(update_fields=['search'])

	def refreshKeywords(self):
		self.keywords = " ".join([
			self.name,
			self.channel,
		])[:200]


class LineItem(models.Model):
	order = models.ForeignKey(Order, related_name='line_items', on_delete=models.CASCADE)
	# change this from shopifysku to externalsku
	shopify_sku = models.ForeignKey(ShopifySKU, related_name='line_items', on_delete=models.CASCADE, null=True)
	num_units = models.IntegerField(null=True)
	# if it's a manual order then the shopify_su and num_units will be null and we will use product and amount instead
	# and then instead of num_units we just straight up have amount?
	product = models.ForeignKey(Product, related_name='line_items', on_delete=models.CASCADE, null=True)
	amount = models.DecimalField(max_digits=10, decimal_places=3, null=True)
