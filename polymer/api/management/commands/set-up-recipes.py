from django.core.management.base import BaseCommand, CommandError
from api.models import *
# from uuid import uuid4
# from dateutil import rrule
# from datetime import datetime, timedelta
# from numpy import median, ceil
# from django.db.models import Count, CharField, Value as V
# from django.db.models.functions import Concat

class Command(BaseCommand):
	help = 'set recipes for polymerstore shopify skus'

	# def add_arguments(self, parser):
	#     parser.add_argument('poll_id', nargs='+', type=int)

	def handle(self, *args, **options):
		team=1

		lemon_curd = Product.objects.filter(name="Lemon curd").first()
		orange_marmalade = Product.objects.filter(name="Orange marmalade").first()
		strawberry_syrup = Product.objects.filter(name="Strawberry syrup").first()

		lemon_curd_shopify = ShopifySKU.objects.filter(name="Lemon curd").first()
		lemon_curd_shopify.product = lemon_curd
		lemon_curd_shopify.save()

		orange_marmalade_shopify = ShopifySKU.objects.filter(name="Orange Marmalade").first()
		orange_marmalade_shopify.product = orange_marmalade
		orange_marmalade_shopify.save()

		strawberry_syrup_shopify = ShopifySKU.objects.filter(name="Strawberry syrup").first()
		strawberry_syrup_shopify.product = strawberry_syrup
		strawberry_syrup_shopify.save()


		lemon_curd_recipe = Recipe.objects.create(product=lemon_curd, default_batch_size=12)
		orange_marmalade_recipe = Recipe.objects.create(product=orange_marmalade, default_batch_size=12)
		strawberry_syrup_recipe = Recipe.objects.create(product=strawberry_syrup, default_batch_size=12)

		strawberries = Product.objects.get(pk=1)
		sugar = Product.objects.get(pk=2)
		corn_syrup = Product.objects.get(pk=3)
		lemon_juice = Product.objects.get(pk=4)
		lemon_zest = Product.objects.get(pk=5)
		salt = Product.objects.get(pk=6)
		oranges = Product.objects.get(pk=7)
		egg_yolks = Product.objects.get(pk=8)
		butter = Product.objects.get(pk=9)

		ing = Ingredient.objects.create(recipe=lemon_curd_recipe, product=lemon_juice, amount=4)
		ing = Ingredient.objects.create(recipe=lemon_curd_recipe, product=lemon_zest, amount=2)
		ing = Ingredient.objects.create(recipe=lemon_curd_recipe, product=egg_yolks, amount=65)
		ing = Ingredient.objects.create(recipe=lemon_curd_recipe, product=sugar, amount=0.34)
		ing = Ingredient.objects.create(recipe=lemon_curd_recipe, product=butter, amount=4)


		ing = Ingredient.objects.create(recipe=strawberry_syrup_recipe, product=lemon_juice, amount=1)
		ing = Ingredient.objects.create(recipe=strawberry_syrup_recipe, product=strawberries, amount=0.5)
		ing = Ingredient.objects.create(recipe=strawberry_syrup_recipe, product=corn_syrup, amount=1.5)
		ing = Ingredient.objects.create(recipe=strawberry_syrup_recipe, product=salt, amount=0.001)
		ing = Ingredient.objects.create(recipe=strawberry_syrup_recipe, product=sugar, amount=0.2)

		ing = Ingredient.objects.create(recipe=orange_marmalade_recipe, product=lemon_juice, amount=1)
		ing = Ingredient.objects.create(recipe=orange_marmalade_recipe, product=lemon_zest, amount=2)
		ing = Ingredient.objects.create(recipe=orange_marmalade_recipe, product=oranges, amount=0.5)
		ing = Ingredient.objects.create(recipe=orange_marmalade_recipe, product=sugar, amount=0.2)







