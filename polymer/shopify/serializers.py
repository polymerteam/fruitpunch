from rest_framework import serializers
from api.models import *
from api.v1.serializers import *

class ShopifyOrderSerializer(serializers.Serializer):
	product = serializers.SerializerMethodField()
	total_amount = serializers.SerializerMethodField()
	customer_list = serializers.SerializerMethodField()

	def get_product(self, obj):
		return ProductSerializer(Product.objects.get(pk=obj['product_id'])).data

	def get_total_amount(self, obj):
		return obj['total_amount'] or 0

	def get_customer_list(self, obj):
		return obj['customer_name_list'] or []



class ShopifySimpleOrderSerializer(serializers.Serializer):
	order_number = serializers.SerializerMethodField()
	order_name = serializers.SerializerMethodField()
	customer_name = serializers.SerializerMethodField()
	line_items = serializers.SerializerMethodField()
	created_at = serializers.SerializerMethodField()

	def get_line_items(self, obj):
		line_item_list = []
		for item in obj['line_items']:
			if item['product_id'] != None:
				product = ProductSerializer(Product.objects.get(pk=item['product_id'])).data
			else:
				product = None
			amount = item['amount']
			line_item_list.append({'product': product, 'shopify_id': item['shopify_id'], 'shopify_name': item['shopify_name'], 'amount': amount})
		return line_item_list

	def get_order_number(self, obj):
		return obj['order_number'] or 0

	def get_order_name(self, obj):
		return obj['order_name'] or ''

	def get_customer_name(self, obj):
		return obj['customer_name']

	def get_created_at(self, obj):
		return obj['created_at']




