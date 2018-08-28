from django.db import models
from django.contrib.auth.models import User
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
	# team = models.ForeignKey(Team, related_name='products', on_delete=models.CASCADE)
	name = models.CharField(max_length=50)
	code = models.CharField(max_length=20)
	icon = models.CharField(max_length=50)
	created_at = models.DateTimeField(default=timezone.now, blank=True)
	unit = models.CharField(max_length=20, default="kilogram")
	is_trashed = models.BooleanField(default=False, db_index=True)

class ShopifySKU(models.Model):
	# team = models.ForeignKey(Team, related_name='shopify_skus', on_delete=models.CASCADE)
	name = models.CharField(max_length=300)
	variant_id = models.CharField(max_length=50, unique=True)
	variant_sku = models.CharField(max_length=100, null=True)
	product = models.ForeignKey(Product, related_name='shopify_skus', on_delete=models.CASCADE, null=True)
	conversion_factor = models.DecimalField(default=1, max_digits=10, decimal_places=6)
	# CHANGE ShopifySKU to ExternalSKU and also include a row with the channel e.g. shopify


class Recipe(models.Model):
	# team = models.ForeignKey(Team, related_name='recipes', on_delete=models.CASCADE)
	product = models.ForeignKey(Product, related_name='recipes', on_delete=models.CASCADE)
	default_batch_size = models.DecimalField(default=1, max_digits=10, decimal_places=3)
	is_trashed = models.BooleanField(default=False, db_index=True)
	created_at = models.DateTimeField(default=timezone.now, blank=True)

class Ingredient(models.Model):
	# team = models.ForeignKey(Team, related_name='ingredients', on_delete=models.CASCADE)
	recipe = models.ForeignKey(Recipe, related_name="ingredients", on_delete=models.CASCADE)
	product = models.ForeignKey(Product, related_name="ingredients", on_delete=models.CASCADE)
	amount = models.DecimalField(default=1, max_digits=10, decimal_places=3)
	is_trashed = models.BooleanField(default=False, db_index=True)

class Batch(models.Model):
	# team = models.ForeignKey(Team, related_name='batches', on_delete=models.CASCADE)
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
	# team = models.ForeignKey(Team, related_name='received_inventory', on_delete=models.CASCADE)
	product = models.ForeignKey(Product, related_name='received_inventory', on_delete=models.CASCADE)
	amount = models.DecimalField(default=1, max_digits=10, decimal_places=3)
	received_at = models.DateTimeField(default=timezone.now, blank=True)
	is_trashed = models.BooleanField(default=False, db_index=True)
	dollar_value = models.DecimalField(max_digits=10, decimal_places=2, null=True)


class Order(models.Model):
	# team = models.ForeignKey(Team, related_name='orders', on_delete=models.CASCADE)
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
	due_date = models.DateTimeField(blank=True, null=True)
	url = models.CharField(max_length=200, blank=True, null=True)
	customer = models.CharField(max_length=150, blank=True, null=True)
	# add in customer name


class LineItem(models.Model):
	# team = models.ForeignKey(Team, related_name='line_items', on_delete=models.CASCADE)
	order = models.ForeignKey(Order, related_name='line_items', on_delete=models.CASCADE)
	# change this from shopifysku to externalsku
	shopify_sku = models.ForeignKey(ShopifySKU, related_name='line_items', on_delete=models.CASCADE, null=True)
	num_units = models.IntegerField(null=True)
	# if it's a manual order then the shopify_su and num_units will be null and we will use product and amount instead
	# and then instead of num_units we just straight up have amount?
	product = models.ForeignKey(Product, related_name='line_items', on_delete=models.CASCADE, null=True)
	amount = models.DecimalField(max_digits=10, decimal_places=3, null=True)


# class UserProfile(models.Model):
# 	USERTYPES = (
# 		('a', 'admin'),
# 		('w', 'worker'),
# 	)

# 	user = models.OneToOneField(User, on_delete=models.CASCADE)
# 	gauth_access_token = models.TextField(null=True)
# 	gauth_refresh_token = models.TextField(null=True)
# 	token_type = models.CharField(max_length=100, null=True) 
# 	expires_in = models.IntegerField(null=True)
# 	expires_at = models.FloatField(null=True)
# 	gauth_email = models.TextField(null=True)
# 	email = models.TextField(null=True)
# 	team = models.ForeignKey(Team, related_name='userprofiles', on_delete=models.CASCADE, null=True)
# 	account_type = models.CharField(max_length=1, choices=USERTYPES, default='a')
# 	send_emails = models.BooleanField(default=True)
# 	last_seen = models.DateTimeField(default=timezone.now)
# 	walkthrough = models.IntegerField(default=1)

