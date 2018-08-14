from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.
class Team(models.Model):
	name = models.CharField(max_length=50, unique=True)
	shopify_access_token = models.TextField(null=True)
	shopify_store_name = models.CharField(max_length=50, null=True)

class Product(models.Model):
	# team = models.ForeignKey(Team, related_name='products', on_delete=models.CASCADE)
	name = models.CharField(max_length=50)
	code = models.CharField(max_length=20)
	icon = models.CharField(max_length=50)
	created_at = models.DateTimeField(default=timezone.now, blank=True)
	unit = models.CharField(max_length=20, default="kilogram")
	dollar_value = models.DecimalField(max_digits=10, decimal_places=2, null=True)
	is_trashed = models.BooleanField(default=False, db_index=True)

class ShopifySKU(models.Model):
	# team = models.ForeignKey(Team, related_name='shopify_skus', on_delete=models.CASCADE)
	name = models.CharField(max_length=50)
	sku = models.CharField(max_length=20, unique=True)
	product = models.ForeignKey(Product, related_name='shopify_skus', on_delete=models.CASCADE, null=True)


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


class ReceivedInventory(models.Model):
	# team = models.ForeignKey(Team, related_name='received_inventory', on_delete=models.CASCADE)
	product = models.ForeignKey(Product, related_name='received_inventory', on_delete=models.CASCADE)
	amount = models.DecimalField(default=1, max_digits=10, decimal_places=3)
	received_at = models.DateTimeField(default=timezone.now, blank=True)
	is_trashed = models.BooleanField(default=False, db_index=True)


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

