from rest_framework import serializers
from api.models import *
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from smtplib import SMTPException
from django.db.models import Count, F, Q, Sum
from datetime import date, datetime, timedelta
import operator
import pytz
import re
import json


class UserSerializer(serializers.ModelSerializer):
	class Meta:
		model = User
		fields = ('id', 'username')

class ProductSerializer(serializers.ModelSerializer):
	class Meta:
		model = Product
		fields = ('id', 'name', 'code', 'icon', 'unit', 'dollar_value', 'is_trashed', 'created_at')

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
		# print(validated_data)
		ingredients = validated_data.pop('ingredients_data')
		# print(validated_data['product'])
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

# class BatchItemSerializer(serializers.ModelSerializer):
# 	batch_id = serializers.PrimaryKeyRelatedField(source='batch', queryset=Batch.objects.all())
# 	product = ProductSerializer(read_only=True)
# 	active_recipe = RecipeSerializer(read_only=True)

# 	class Meta:
# 		model = BatchItem
# 		fields = ('id', 'batch_id', 'product', 'active_recipe', 'amount', 'is_trashed')


class BatchSerializer(serializers.ModelSerializer):
	# batch_items = BatchItemSerializer(many=True, read_only=True)
	product = ProductSerializer(read_only=True)
	# product_id = serializers.PrimaryKeyRelatedField(source='product', queryset=Product.objects.all(), write_only=True)
	active_recipe = RecipeSerializer(read_only=True)

	def create(self, validated_data):
		product = validated_data['product']
		active_recipe = Recipe.objects.filter(is_trashed=False, product=product)
		if active_recipe.count() > 0:
			active_recipe = active_recipe.first()
		else:
			active_recipe = None
		new_batch = Batch.objects.create(**validated_data, active_recipe=active_recipe)
		return new_batch

	class Meta:
		model = Batch
		fields = ('id', 'status', 'started_at', 'completed_at', 'is_trashed', 'product', 'active_recipe', 'amount')


	product = models.ForeignKey(Product, related_name="batch_items", on_delete=models.CASCADE)
	active_recipe = models.ForeignKey(Recipe, related_name="batch_items", on_delete=models.CASCADE, null=True)
	amount = models.DecimalField(default=1, max_digits=10, decimal_places=3)
	is_trashed = models.BooleanField(default=False, db_index=True)



# class BatchCreateWithItemsSerializer(serializers.ModelSerializer):
# 	batch_items = BatchItemSerializer(many=True, read_only=True)
# 	batch_items_data = serializers.CharField(write_only=True)

# 	def create(self, validated_data):
# 		print(validated_data)
# 		batch_items = validated_data.pop('batch_items_data')
# 		batch_items = json.loads((batch_items))
# 		new_batch = Batch.objects.create(**validated_data)
# 		for batch_item in batch_items:
# 			print(batch_item['product'])
# 			product = Product.objects.get(pk=batch_item['product'])
# 			amount = batch_item['amount']
# 			active_recipe = Recipe.objects.filter(is_trashed=False, product=product)
# 			if active_recipe.count() > 0:
# 				active_recipe = active_recipe.first()
# 			else:
# 				active_recipe = None
# 			b_i = BatchItem.objects.create(batch=new_batch, product=product, active_recipe=active_recipe, amount=amount)
# 		return new_batch

	# class Meta:
	# 	model = Batch
	# 	extra_kwargs = {'batch_items_data': {'write_only': True}}
	# 	fields = ('id', 'status', 'started_at', 'completed_at', 'is_trashed', 'batch_items', 'batch_items_data')



class InventorySerializer(serializers.ModelSerializer):
	in_progress_amount = serializers.DecimalField(max_digits=10, decimal_places=3)
	completed_amount = serializers.DecimalField(max_digits=10, decimal_places=3)
	received_amount = serializers.DecimalField(max_digits=10, decimal_places=3)
	asdf = serializers.DecimalField(max_digits=10, decimal_places=3)
	product = serializers.SerializerMethodField()

	def get_product(self, product):
		return ProductSerializer(Product.objects.get(pk=product['id'])).data

	class Meta:
		model = Product
		fields = ('id', 'product', 'in_progress_amount', 'completed_amount', 'received_amount', 'asdf')


class ReceivedInventorySerializer(serializers.ModelSerializer):
	product = ProductSerializer(read_only=True)
	product_id = serializers.PrimaryKeyRelatedField(source='product', queryset=Product.objects.all(), write_only=True)
	
	def __init__(self, *args, **kwargs):
		many = kwargs.pop('many', True)
		super(ReceivedInventorySerializer, self).__init__(many=many, *args, **kwargs)

	class Meta:
		model = ReceivedInventory
		fields = ('id', 'product', 'product_id', 'amount', 'received_at', 'is_trashed')


# class UserProfileSerializer(serializers.ModelSerializer):
# 	user_id = serializers.CharField(source='user.id', read_only=True)
# 	username = serializers.CharField(source='user.username', read_only=True)
# 	first_name = serializers.CharField(source='user.first_name')
# 	last_name = serializers.CharField(source='user.last_name')

# 	class Meta:
# 		model = UserProfile
# 		fields = ('user_id', 'id', 'username', 'first_name', 'last_name')



# class ProcessTypeWithUserSerializer(serializers.ModelSerializer):
# 	attributes = serializers.SerializerMethodField()
# 	created_by_name = serializers.CharField(source='created_by.username', read_only=True)
# 	username = serializers.SerializerMethodField(source='get_username', read_only=True)
# 	last_used = serializers.DateTimeField(source='get_last_used_date', read_only=True)
# 	team_created_by_name = serializers.CharField(source='team_created_by.name', read_only=True)
# 	created_at = serializers.DateTimeField(read_only=True)
# 	default_amount = serializers.DecimalField(max_digits=10, decimal_places=3, coerce_to_string=False)

# 	def get_attributes(self, process_type):
# 		return AttributeSerializer(process_type.attribute_set.order_by('rank'), many=True).data

# 	def get_username(self, product):
# 		username = product.created_by.username
# 		return re.sub('_\w+$', '', username)

# 	class Meta:
# 		model = ProcessType
# 		fields = ('id', 'username', 'name', 'code', 'icon', 'attributes', 'unit', 'created_by', 'output_desc', 'created_by_name', 'default_amount', 'team_created_by', 'team_created_by_name', 'is_trashed', 'created_at', 'last_used', 'search', 'category')
