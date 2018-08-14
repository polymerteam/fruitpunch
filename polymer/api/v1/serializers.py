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

class TeamSerializer(serializers.ModelSerializer):
	class Meta:
		model = Team
		fields = ('id', 'name', 'shopify_store_name', 'shopify_access_token')

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


class BatchSerializer(serializers.ModelSerializer):
	product = ProductSerializer(read_only=True)
	active_recipe = RecipeSerializer(read_only=True)

	def create(self, validated_data):
		product = validated_data['product']
		active_recipe = Recipe.objects.filter(is_trashed=False, product=product).order_by('-created_at')
		if active_recipe.count() > 0:
			active_recipe = active_recipe.first()
		else:
			active_recipe = None
		new_batch = Batch.objects.create(**validated_data, active_recipe=active_recipe)
		return new_batch

	class Meta:
		model = Batch
		fields = ('id', 'status', 'started_at', 'completed_at', 'is_trashed', 'product', 'active_recipe', 'amount')


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

