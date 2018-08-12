from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.

class Product(models.Model):
	# team = models.ForeignKey(Team, related_name='processes', on_delete=models.CASCADE)
	name = models.CharField(max_length=50)
	code = models.CharField(max_length=20)
	icon = models.CharField(max_length=50)
	created_at = models.DateTimeField(default=timezone.now, blank=True)
	unit = models.CharField(max_length=20, default="kilogram")
	dollar_value = models.DecimalField(max_digits=10, decimal_places=2, null=True)
	is_trashed = models.BooleanField(default=False, db_index=True)


class Recipe(models.Model):
	# team = models.ForeignKey(Team, related_name='processes', on_delete=models.CASCADE)
	product = models.ForeignKey(Product, related_name='recipes', on_delete=models.CASCADE)
	default_batch_size = models.DecimalField(default=1, max_digits=10, decimal_places=3)
	is_trashed = models.BooleanField(default=False, db_index=True)
	created_at = models.DateTimeField(default=timezone.now, blank=True)

class Ingredient(models.Model):
	# team = models.ForeignKey(Team, related_name='processes', on_delete=models.CASCADE)
	recipe = models.ForeignKey(Recipe, related_name="ingredients", on_delete=models.CASCADE)
	product = models.ForeignKey(Product, related_name="ingredients", on_delete=models.CASCADE)
	amount = models.DecimalField(default=1, max_digits=10, decimal_places=3)
	is_trashed = models.BooleanField(default=False, db_index=True)

class Batch(models.Model):
	# team = models.ForeignKey(Team, related_name='processes', on_delete=models.CASCADE)
	STATUSES = (
		('i', 'in progress'),
		('c', 'completed')
	)
	status = models.CharField(max_length=1, choices=STATUSES, default='i')
	# recipe = models.ForeignKey(Recipe, related_name="batches", on_delete=models.CASCADE)
	# product = models.ForeignKey(Product, related_name="batches", on_delete=models.CASCADE)
	# amount = models.DecimalField(default=1, max_digits=10, decimal_places=3)
	started_at = models.DateTimeField(default=timezone.now, blank=True)
	completed_at = models.DateTimeField(blank=True, null=True)
	is_trashed = models.BooleanField(default=False, db_index=True)


class BatchItem(models.Model):
	# team = models.ForeignKey(Team, related_name='processes', on_delete=models.CASCADE)
	batch = models.ForeignKey(Batch, related_name="batch_items", on_delete=models.CASCADE)
	product = models.ForeignKey(Product, related_name="batch_items", on_delete=models.CASCADE)
	active_recipe = models.ForeignKey(Recipe, related_name="batch_items", on_delete=models.CASCADE, null=True)
	amount = models.DecimalField(default=1, max_digits=10, decimal_places=3)
	is_trashed = models.BooleanField(default=False, db_index=True)

class ReceivedInventory(models.Model):
	# team = models.ForeignKey(Team, related_name='processes', on_delete=models.CASCADE)
	product = models.ForeignKey(Product, related_name='received_inventory', on_delete=models.CASCADE)
	amount = models.DecimalField(default=1, max_digits=10, decimal_places=3)
	received_at = models.DateTimeField(default=timezone.now, blank=True)
	is_trashed = models.BooleanField(default=False, db_index=True)


# class Team(models.Model):
# 	name = models.CharField(max_length=50, unique=True)
# 	timezone = models.CharField(max_length=50, default=pytz.timezone('US/Pacific').zone)
# 	task_label_type = models.IntegerField(default=0)
# 	time_format = models.CharField(max_length=1, choices=TIME_FORMATS, default='n')

# 	def __str__(self):
# 		return self.name

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

