# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import csv

from api.models import *
# from api.v1.serializers import *
from shopify.serializers import *
from django.http import HttpResponse
from requests_oauthlib import OAuth2Session, TokenUpdated
from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response
import requests
import datetime
import random
import simplejson as json


SHOPIFY_SCOPE = 'read_all_orders,read_orders,write_orders,read_products,read_customers'
REDIRECT_URI = 'https://localhost:3000/shopify/ext'

# @csrf_exempt
@api_view(['POST'])
def createShopifyAuthURL(request):
	shop_name = request.data['shopname']
	if 'team' in request.data:
		team_id = request.data['team']
	else:
		team_id = 1
	team = Team.objects.get(pk=team_id)
	team.shopify_store_name = shop_name
	team.save()
	# save the shop name to the user
  # state = ''.join(random.sample('0123456789', 5))
	state = '543234'
	authorization_base_url = "https://" + shop_name + ".myshopify.com/admin/oauth/authorize"

	shopify = OAuth2Session(settings.SHOPIFY_API_KEY, redirect_uri=REDIRECT_URI, scope=SHOPIFY_SCOPE)
	authorization_url, state = shopify.authorization_url(authorization_base_url, state=state)
	response = HttpResponse(authorization_url, content_type="text/plain")
	return response

# @csrf_exempt
@api_view(['POST'])
def createShopifyAuthToken(request):
	# shop_name = request.data['shopname']
	# shop_name = 'polymerstore'

	auth_response = request.data['auth_response']
	code_str = auth_response.split("code=",1)[1]
	code = code_str.split("&",1)[0]
	shopname_str = auth_response.split("shop=",1)[1]
	shop_name = shopname_str.split(".myshopify",1)[0]

	token_url = "https://" + shop_name + ".myshopify.com/admin/oauth/access_token"

  # user_id = request.POST.get('user_id')
	shopify = OAuth2Session(settings.SHOPIFY_API_KEY,
		redirect_uri=REDIRECT_URI,
		scope=SHOPIFY_SCOPE)
	token = shopify.fetch_token(token_url,
		code=code,
		client_secret=settings.SHOPIFY_SECRET_KEY)
	if 'team' in request.data:
		team_id = request.data['team']
	else:
		team_id = 1
	team = Team.objects.get(pk=team_id)
	team.shopify_store_name = shop_name
	team.shopify_access_token = token['access_token']
	team.save()
  # save the token to the user
  # success response
	response = HttpResponse(json.dumps({"token": token['access_token']}), content_type="text/plain")
	return response;




@api_view(['GET'])
def getShopifyProducts(request):	
	body = shopifyAPIHelper(request, "admin/products.json?fields=id,title,variants")
	shopify_products = body['products']
	for shopify_product in shopify_products:
		main_title = shopify_product['title']
		for variant in shopify_product['variants']:
			variant_title = main_title
			if variant['title'] != "Default Title":
				variant_title = main_title + " - " + variant['title']
			variant_id = variant['id']
			variant_sku = variant['sku']
			shopifysku = ShopifySKU.objects.filter(variant_id=variant_id)
			if shopifysku.count() == 0:
				ShopifySKU.objects.create(name=variant_title, variant_id=variant_id, variant_sku=variant_sku)
			else:
				sp = shopifysku.first()
				was_updated = False
				if sp.name != variant_title:
					sp.name = variant_title
					was_updated = True
				if sp.variant_sku != variant_sku:
					sp.variant_sku = variant_sku
					was_updated = True
				if was_updated:
					sp.save()
	# filter by team
	queryset = ShopifySKU.objects.all()
	serializer = ShopifySKUSerializer(queryset, many=True)
	return Response(serializer.data)

	# response = HttpResponse(json.dumps({"body": body}), content_type="text/plain")
	# return response;
@api_view(['GET'])
def getIngredientsForOrders(request):
	order_list = shopifyOrdersByProductHelper(request)

	ingredient_amount_map = {}
	for item in order_list:
		product = item['product_id']
		# the total amount is already the shopify amount multiplied by the shopify to polymer conversion - e.g. 1 orange marmalade on shopify is x polymer orange marmalade units
		amt = item['total_amount']
		matching_recipe = Recipe.objects.filter(is_trashed=False, product=product).order_by('-created_at').first()
		recipe_size = matching_recipe.default_batch_size
		ingredients = Ingredient.objects.filter(recipe=matching_recipe, is_trashed=False)
		for ingredient in ingredients:
			added_amt = (ingredient.amount/recipe_size)*amt
			if ingredient.product.id in ingredient_amount_map:
				ingredient_amount_map[ingredient.product.id] += added_amt
			else:
				ingredient_amount_map[ingredient.product.id] = added_amt
	ing_list = []
	for obj in ingredient_amount_map:
		qs = Product.objects.filter(pk=obj).annotate(in_progress_amount=Coalesce(Sum('batches__amount', filter=Q(batches__status='i')), 0))
		qs = qs.annotate(completed_amount=Coalesce(Sum('batches__amount', filter=Q(batches__status='c')), 0))
		qs = qs.annotate(received_amount_total=Coalesce(Sum('received_inventory__amount'), 0))
		
		amount_used = Batch.objects.filter(is_trashed=False, status='c')\
			.annotate(ingredient_amount=Sum('active_recipe__ingredients__amount', filter=Q(active_recipe__ingredients__product__id=obj)))\
			.annotate(recipe_batch_size=F('active_recipe__default_batch_size'))\
			.annotate(amt_in_batch=F('amount')*F('ingredient_amount')/F('recipe_batch_size'))\
			.aggregate(Sum('amt_in_batch'))
		if not amount_used['amt_in_batch__sum']:
			amount_used = 0
		else:
			amount_used = amount_used['amt_in_batch__sum']
		inventory_amount = qs[0].received_amount_total - amount_used + qs[0].completed_amount

		ing_list.append({'product_id': obj, 'amount_needed': ingredient_amount_map[obj], 'amount_in_inventory': inventory_amount})

	serializer = IngredientAmountSerializer(ing_list, many=True)
	return Response(serializer.data)

@api_view(['GET'])
def getShopifyOrdersByProduct(request):	
	order_list = shopifyOrdersByProductHelper(request)
	serializer = ShopifyOrderSerializer(order_list, many=True)
	return Response(serializer.data)


def formatCustomerName(order):
	if 'customer' in order:
		if order['customer']['first_name'] and order['customer']['first_name'] != '':
			customer_name = order['customer']['first_name']
		if order['customer']['last_name'] and order['customer']['last_name'] != '':
			customer_name += ' ' + order['customer']['last_name']
	else:
		customer_name = None
	return customer_name

def getOrCreateOrder(orders, status):
	order_ids = []
	for order in orders:
		customer_name = formatCustomerName(order)
		order_number = order['order_number']
		order_name = order['name']
		order_date = order['created_at']
		status_url = order['order_status_url']

		matching_orders = Order.objects.filter(channel='shopify', number=order_number).order_by('-created_at')
		if matching_orders.count() > 0:
			new_order = matching_orders.first()
			new_order.status = status
			new_order.save()
		else:
			new_order = Order.objects.create(channel='shopify', number=order_number, name=order_name, created_at=order_date, url=status_url, status=status)

		order_ids.append(new_order.id)

		for line_item in order['line_items']:
			variant_id = line_item['variant_id']
			quantity = line_item['quantity']
			matching_sku = ShopifySKU.objects.filter(variant_id=variant_id).first()

			new_li = LineItem.objects.get_or_create(order=new_order, shopify_sku=matching_sku, num_units=quantity)

	return order_ids

@api_view(['GET'])
def loadShopifyOrdersIntoPolymer(request):
	# get all open orders
	body = shopifyAPIHelper(request, "admin/orders.json")
	open_shopify_orders = body['orders']
	open_order_ids = getOrCreateOrder(open_shopify_orders, 'i')

	body = shopifyAPIHelper(request, "admin/orders.json?status=closed")
	closed_shopify_orders = body['orders']
	closed_order_ids = getOrCreateOrder(closed_shopify_orders, 'c')

	# maybe delete the cancelled orders instead???
	body = shopifyAPIHelper(request, "admin/orders.json?status=cancelled")
	cancelled_shopify_orders = body['orders']
	cancelled_order_ids = getOrCreateOrder(cancelled_shopify_orders, 'x')

	orders = Order.objects.filter(pk__in=open_order_ids)

	serializer = OrderSerializer(orders, many=True)
	return Response(serializer.data)


def getProductFromSKU(variant_id):
	matching_products = ShopifySKU.objects.filter(variant_id=variant_id)
	matching_product_id = None
	conversion_factor = None
	if matching_products.count() > 0:
		matching_product = matching_products.first().product
		conversion_factor = matching_products.first().conversion_factor
		if matching_product:
			matching_product_id = matching_product.id
	return matching_product_id, conversion_factor

def shopifyOrdersByProductHelper(request):
	body = shopifyAPIHelper(request, "admin/orders.json")
	shopify_orders = body['orders']
	order_map = {}
	customer_map = {}
	for order in shopify_orders:
		customer_name = formatCustomerName(order)
		for line_item in order['line_items']:
			variant_id = line_item['variant_id']
			quantity = line_item['quantity']
			matching_product, conversion_factor = getProductFromSKU(variant_id)
			if matching_product:
				if matching_product in order_map:
					order_map[matching_product] += quantity*conversion_factor
				else:
					order_map[matching_product] = quantity*conversion_factor
					customer_map[matching_product] = []
				customer_map[matching_product].append(customer_name)
	order_list = []
	for obj in order_map:
		order_list.append({'product_id': obj, 'total_amount': order_map[obj], 'customer_name_list': customer_map[obj]})
	return order_list

@api_view(['GET'])
def getShopifyOrders(request):	
	body = shopifyAPIHelper(request, "admin/orders.json")
	shopify_orders = body['orders']
	order_list = []
	for order in shopify_orders:
		customer_name = formatCustomerName(order)
		order_number = order['order_number']
		order_name = order['name']
		order_date = order['created_at']
		line_item_list = []
		for line_item in order['line_items']:
			variant_id = line_item['variant_id']
			quantity = line_item['quantity']
			shopify_item_name = line_item['name']
			matching_product, conversion_factor = getProductFromSKU(variant_id)
			if matching_product:
				polymer_amount = conversion_factor*quantity
			else:
				polymer_amount = None
			line_item_list.append({'product_id': matching_product, 'shopify_id': variant_id, 'shopify_name': shopify_item_name, 'amount': quantity, 'polymer_amount': polymer_amount})
		order_list.append({'order_number': order_number, 'order_name': order_name, 'created_at': order_date, 'customer_name': customer_name, 'line_items': line_item_list})

	serializer = ShopifySimpleOrderSerializer(order_list, many=True)
	return Response(serializer.data)

def shopifyAPIHelper(request, url):
	team_id = request.query_params.get('team')
	team = Team.objects.get(pk=team_id)
	shop_name = team.shopify_store_name
	access_token = team.shopify_access_token
	# shop_name = 'polymerstore'
	api_url = "https://" + shop_name + ".myshopify.com/" + url
	token_url = "https://" + shop_name + ".myshopify.com/admin/oauth/access_token"

	token = {
		'access_token': access_token
	}
	extra = {
		'client_id': settings.SHOPIFY_API_KEY,
		'client_secret': settings.SHOPIFY_SECRET_KEY
	}
	extra_params = {'X-Shopify-Access-Token': access_token}

	try:
		shopify = OAuth2Session(settings.SHOPIFY_API_KEY, token=token, auto_refresh_url=token_url, auto_refresh_kwargs=extra, scope=SHOPIFY_SCOPE)
		random_data = shopify.get(api_url, headers=extra_params)

	except TokenUpdated as e:
		team.shopify_access_token = e.token
		team.save()
	r1 = shopify.get(api_url, headers=extra_params)
	body = json.loads(r1.content)
	return body


# def update_userprofile_token(user_profile, token):
# 	user_profile.gauth_access_token = token['access_token']
# 	user_profile.gauth_refresh_token = token['refresh_token']
# 	user_profile.expires_in = token['expires_in']
# 	user_profile.expires_at = token['expires_at']


# # @csrf_exempt
# @api_view(['POST'])
# def clearToken(request):
# 	user_id = request.POST.get('user_id')
# 	user_profile = UserProfile.objects.get(user=user_id)
# 	user_profile.gauth_access_token = ""
# 	user_profile.gauth_email = ""
# 	user_profile.save()
# 	response = HttpResponse(serializers.serialize('json', [user_profile]))
# 	return response


