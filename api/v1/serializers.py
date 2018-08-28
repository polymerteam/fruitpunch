from rest_framework import serializers
from api.models import *
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from smtplib import SMTPException
from django.db.models import Count, F, Q, Sum, Avg, ExpressionWrapper
from datetime import date, datetime, timedelta
import operator
import pytz
import re
import json


class UserSerializer(serializers.ModelSerializer):
	class Meta:
		model = User
		fields = ('id', 'username')

class UserLoginSerializer(serializers.ModelSerializer):
	team_name = serializers.CharField(source='userprofile.team.name')
	team = serializers.CharField(source='userprofile.team.id', read_only=True)
	account_type = serializers.CharField(source='userprofile.account_type', read_only=True)
	profile_id = serializers.CharField(source='userprofile.id')
	user_id = serializers.CharField(source='userprofile.user.id')
	shopify_access_token = serializers.CharField(source='userprofile.team.shopify_access_token')
	shopify_store_name = serializers.CharField(source='userprofile.team.shopify_store_name')

	class Meta:
		model = User
		fields = ('user_id', 'profile_id', 'username', 'first_name', 'last_name', 'team', 'account_type', 'team_name', 'shopify_access_token', 'shopify_store_name')

def sendEmail(userprofile_id):
  userprofile = UserProfile.objects.get(pk=userprofile_id)
  team_name = userprofile.team.name
  email = userprofile.email

  link = "https://asdf.asdf.com/join/" + str(userprofile_id) + "/"

  subject = "You're invited to team " + team_name + " on Polymer!"
  message = ""
  html_message = "You have been invited to join team: <b>" + team_name + '</b> on Polymer. Click the link to accept your invitation and set your username/password. ' + link
  try:
    send_mail(
        subject,
        message,
        'admin@polymerize.co',
        [email],
        fail_silently=False,
        html_message=html_message,
    )
  except SMTPException as e:
    print('send_mail failed: ', e)

class UserProfileCreateSerializer(serializers.ModelSerializer):
	username = serializers.CharField(source='user.username')
	password = serializers.CharField(source='user.password')
	first_name = serializers.CharField(source='user.first_name')
	last_name = serializers.CharField(source='user.last_name')
	team_name = serializers.CharField(source='team.name', read_only=True)
	profile_id = serializers.CharField(source='id', read_only=True)

	def create(self, validated_data):
		team = validated_data['team']
		data = validated_data['user']
		long_username = data['username'].lower() + '_' + team.name

		# create the user 
		user = User.objects.create(username=long_username, first_name=data['first_name'], last_name=data['last_name'])
		user.set_password(data.get('password'))
		user.save()

		# create the userprofile
		account_type = validated_data.get('account_type', 'a')
		email = validated_data.get('email', '')
		invited = validated_data.get('invited', False)

		userprofile = UserProfile.objects.create(
			user=user,
			team=team,
			account_type=account_type,
			email=email,
		)

		if invited:
			sendEmail(userprofile.id)

		return userprofile

	class Meta:
		model = UserProfile
		extra_kwargs = {'account_type': {'write_only': True}, 'password': {'write_only': True}, 'invited': {'write_only': True}}
		fields = ('id', 'profile_id', 'username', 'password', 'first_name', 'last_name', 'team', 'account_type', 'team_name', 'email')


class UserProfileSerializer(serializers.ModelSerializer):
	team_name = serializers.CharField(source='team.name', read_only=True)
	team = serializers.CharField(source='team.id', read_only=True)
	profile_id = serializers.CharField(source='id', read_only=True)
	user_id = serializers.CharField(source='user.id', read_only=True)
	username = serializers.CharField(source='user.username', read_only=True)
	username_display = serializers.CharField(source='get_username_display', read_only=True)
	first_name = serializers.CharField(source='user.first_name')
	last_name = serializers.CharField(source='user.last_name')
	shopify_access_token = serializers.CharField(source='userprofile.team.shopify_access_token')

	class Meta:
		model = UserProfile
		fields = ('user_id', 'id', 'profile_id', 'username', 'username_display', 'first_name', 'last_name', 'team', 'account_type', 'team_name', 'email', 'shopify_access_token')


class TeamSerializer(serializers.ModelSerializer):
	class Meta:
		model = Team
		fields = ('id', 'name', 'shopify_store_name', 'shopify_access_token')

class ProductSerializer(serializers.ModelSerializer):
	def __init__(self, *args, **kwargs):
		many = kwargs.pop('many', False)
		super(ProductSerializer, self).__init__(many=many, *args, **kwargs)

	class Meta:
		model = Product
		fields = ('id', 'name', 'code', 'icon', 'unit', 'is_trashed', 'created_at', 'team')

class ShopifySKUSerializer(serializers.ModelSerializer):
	product = ProductSerializer(read_only=True)
	product_id = serializers.PrimaryKeyRelatedField(source='product', queryset=Product.objects.all(), write_only=True)
	class Meta:
		model = ShopifySKU
		fields = ('id', 'name', 'variant_id', 'variant_sku', 'product', 'product_id', 'conversion_factor', 'team')

class IngredientSerializer(serializers.ModelSerializer):
	product = ProductSerializer(read_only=True)
	product_id = serializers.PrimaryKeyRelatedField(source='product', queryset=Product.objects.all(), write_only=True)
	recipe_id = serializers.PrimaryKeyRelatedField(source='recipe', queryset=Recipe.objects.all())

	class Meta:
		model = Ingredient
		fields = ('id', 'product', 'product_id', 'amount', 'recipe_id', 'is_trashed')


class RecipeSerializer(serializers.ModelSerializer):
	product = ProductSerializer(read_only=True)
	product_id = serializers.PrimaryKeyRelatedField(source='product', queryset=Product.objects.all(), write_only=True)
	ingredients = IngredientSerializer(many=True, read_only=True)

	class Meta:
		model = Recipe
		fields = ('id', 'product', 'product_id', 'default_batch_size', 'is_trashed', 'created_at', 'ingredients')

class RecipeCreateWithIngredientsSerializer(serializers.ModelSerializer):
	product = ProductSerializer(read_only=True)
	product_id = serializers.PrimaryKeyRelatedField(source='product', queryset=Product.objects.all(), write_only=True)
	ingredients = IngredientSerializer(many=True, read_only=True)
	ingredients_data = serializers.CharField(write_only=True)

	def create(self, validated_data):
		ingredients = validated_data.pop('ingredients_data')
		matching_recipes = Recipe.objects.filter(product=validated_data['product'], is_trashed=False)
		if matching_recipes.count() > 0:
			raise serializers.ValidationError({'product': 'A recipe already exists for this Product'})
			return
		ingredients = json.loads((ingredients))#.decode("utf-8"))
		new_recipe = Recipe.objects.create(**validated_data)
		for ingredient in ingredients:
			product = Product.objects.get(pk=ingredient['product'])
			amount = ingredient['amount']
			ing = Ingredient.objects.create(recipe=new_recipe, product=product, amount=amount)
		return new_recipe

	class Meta:
		model = Recipe
		extra_kwargs = {'ingredients_data': {'write_only': True}}
		fields = ('id', 'product', 'product_id', 'default_batch_size', 'is_trashed', 'created_at', 'ingredients', 'ingredients_data')


class BatchSerializer(serializers.ModelSerializer):
	product = ProductSerializer(read_only=True)
	active_recipe = RecipeSerializer(read_only=True)
	product_data = serializers.CharField(write_only=True)

	def create(self, validated_data):
		product = validated_data.pop('product_data')
		active_recipe = Recipe.objects.filter(is_trashed=False, product=product).order_by('-created_at')
		if active_recipe.count() > 0:
			active_recipe = active_recipe.first()
		else:
			active_recipe = None
		product_obj = Product.objects.get(pk=product)
		new_batch = Batch.objects.create(**validated_data, product=product_obj, active_recipe=active_recipe)
		return new_batch

	class Meta:
		model = Batch
		extra_kwargs = {'product_data': {'write_only': True}}
		fields = ('id', 'status', 'started_at', 'completed_at', 'is_trashed', 'product', 'active_recipe', 'amount', 'product_data', 'calendar_start', 'calendar_end')


class InventorySerializer(serializers.ModelSerializer):
	in_progress_amount = serializers.DecimalField(max_digits=10, decimal_places=3)
	available_amount = serializers.DecimalField(max_digits=10, decimal_places=3)
	# completed_amount = serializers.DecimalField(max_digits=10, decimal_places=3)
	# received_amount = serializers.DecimalField(max_digits=10, decimal_places=3)
	product = serializers.SerializerMethodField()

	def get_product(self, product):
		return ProductSerializer(Product.objects.get(pk=product['id'])).data

	class Meta:
		model = Product
		fields = ('id', 'product', 'in_progress_amount', 'available_amount')
		# fields = ('id', 'product', 'in_progress_amount', 'completed_amount', 'received_amount')


class ReceivedInventorySerializer(serializers.ModelSerializer):
	product = ProductSerializer(read_only=True)
	product_id = serializers.PrimaryKeyRelatedField(source='product', queryset=Product.objects.all(), write_only=True)
	
	def __init__(self, *args, **kwargs):
		many = kwargs.pop('many', True)
		super(ReceivedInventorySerializer, self).__init__(many=many, *args, **kwargs)

	class Meta:
		model = ReceivedInventory
		fields = ('id', 'product', 'product_id', 'amount', 'dollar_value', 'received_at', 'is_trashed')


class LineItemSerializer(serializers.ModelSerializer):
	shopify_sku = ShopifySKUSerializer(read_only=True)
	shopify_sku_id = serializers.PrimaryKeyRelatedField(source='shopify_sku', queryset=ShopifySKU.objects.all(), write_only=True)
	product = ProductSerializer(read_only=True)
	product_id = serializers.PrimaryKeyRelatedField(source='product', queryset=Product.objects.all(), write_only=True)
	order_id = serializers.PrimaryKeyRelatedField(source='order', queryset=Order.objects.all())

	class Meta:
		model = LineItem
		fields = ('id', 'shopify_sku', 'shopify_sku_id', 'num_units', 'product', 'product_id', 'amount', 'order_id')


class OrderSerializer(serializers.ModelSerializer):
	line_items = LineItemSerializer(many=True, read_only=True)

	class Meta:
		model = Order
		fields = ('id', 'status', 'name', 'number', 'channel', 'customer', 'created_at', 'due_date', 'url', 'line_items', 'team')


class OrderCreateWithLineItemsSerializer(serializers.ModelSerializer):
	line_items = LineItemSerializer(many=True, read_only=True)
	line_items_data = serializers.CharField(write_only=True)

	def create(self, validated_data):
		line_items = validated_data.pop('line_items_data')
		line_items = json.loads(line_items)
		renumber = False
		if 'number' in validated_data:
			matching_order_nums = Order.objects.filter(number=validated_data['number'], channel='manual').count()
			if matching_order_nums > 0:
				renumber = True
		if 'number' not in validated_data or renumber:
			last_order = Order.objects.filter(number__isnull=False, channel='manual').order_by('-number')
			highest_number = 0
			if last_order.count() > 0:
				highest_number = last_order.first().number
			validated_data['number'] = highest_number + 1
		if 'name' not in validated_data:
			validated_data['name'] = 'Manual Order ' + str(validated_data['number'])
		if 'created_at' not in validated_data:
			validated_data['created_at'] = datetime.today()

		order = Order.objects.create(**validated_data)

		for line_item in line_items:
			product = Product.objects.get(pk=line_item['product'])
			amount = line_item['amount']
			LineItem.objects.create(order=order, product=product, amount=amount, shopify_sku=None, num_units=None)
		return order

	class Meta:
		model = Order
		extra_kwargs = {'line_items_data': {'write_only': True}}
		fields = ('id', 'status', 'name', 'number', 'channel', 'created_at', 'due_date', 'url', 'line_items', 'line_items_data', 'team')




