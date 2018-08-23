from rest_framework import serializers
from api.models import *
from api.v1.serializers import *
from django.db.models import OuterRef, Subquery, DecimalField
from django.db.models.functions import Coalesce

class ShopifyOrderSerializer(serializers.Serializer):
	product = serializers.SerializerMethodField()
	total_amount = serializers.IntegerField()
	customer_list = serializers.SerializerMethodField()

	def get_product(self, obj):
		return ProductSerializer(Product.objects.get(pk=obj['product_id'])).data

	def get_customer_list(self, obj):
		return obj['customer_name_list'] or []

class IngredientAmountSerializer(serializers.Serializer):
	product = serializers.SerializerMethodField()
	amount_needed = serializers.DecimalField(max_digits=10, decimal_places=3, coerce_to_string=False)
	amount_in_inventory = serializers.DecimalField(max_digits=10, decimal_places=3, coerce_to_string=False)

	def get_product(self, obj):
		return ProductSerializer(Product.objects.get(pk=obj['product_id'])).data


class ShopifySimpleOrderSerializer(serializers.Serializer):
	order_number = serializers.IntegerField()
	order_name = serializers.CharField()
	customer_name = serializers.CharField()
	line_items = serializers.SerializerMethodField()
	created_at = serializers.DateTimeField()

	def get_line_items(self, obj):
		line_item_list = []
		for item in obj['line_items']:
			if item['product_id'] != None:
				product = ProductSerializer(Product.objects.get(pk=item['product_id'])).data
			else:
				product = None
			amount = item['amount']
			line_item_list.append({'product': product, 'shopify_id': item['shopify_id'], 'shopify_name': item['shopify_name'], 'amount': amount, 'polymer_amount': item['polymer_amount']})
		return line_item_list





