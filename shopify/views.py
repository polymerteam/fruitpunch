# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import csv

from api.models import *
from api.v1.views import *
# from api.v1.serializers import *
from shopify.serializers import *
from django.http import HttpResponse, HttpResponseForbidden
from requests_oauthlib import OAuth2Session, TokenUpdated
from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response
import requests
import datetime
import random
import simplejson as json
from django.contrib.postgres.aggregates.general import ArrayAgg



SHOPIFY_SCOPE = 'read_all_orders,read_orders,read_products,read_customers'
REDIRECT_URI = settings.REDIRECT_URI

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
	response = HttpResponse(json.dumps({"token": token['access_token']}), content_type="application/json")
	return response;




@api_view(['GET'])
def getShopifyProducts(request):	
	body = shopifyAPIHelper(request, "admin/products.json?fields=id,title,variants")
	team_id = request.query_params.get('team')
	team = Team.objects.get(pk=team_id)
	shopify_products = body['products']
	for shopify_product in shopify_products:
		main_title = shopify_product['title']
		for variant in shopify_product['variants']:
			variant_title = main_title
			if variant['title'] != "Default Title":
				variant_title = main_title + " - " + variant['title']
			variant_id = variant['id']
			variant_sku = variant['sku']
			shopifysku = ShopifySKU.objects.filter(variant_id=variant_id, team=team, channel='shopify')
			if shopifysku.count() == 0:
				ShopifySKU.objects.create(name=variant_title, variant_id=variant_id, variant_sku=variant_sku, team=team, channel='shopify')
			else:
				sp = shopifysku.first()
				was_updated = False
				if sp.name != variant_title:
					sp.name = variant_title
					was_updated = True
				if sp.variant_sku != variant_sku:
					sp.variant_sku = variant_sku
					was_updated = True
				if sp.team != team:
					sp.team = team
					was_updated = True
				if was_updated:
					sp.save()
	# filter by team
	queryset = ShopifySKU.objects.filter(team=team, channel='shopify')
	serializer = ShopifySKUSerializer(queryset, many=True)
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

def getOrCreateOrder(orders, status, team):
	order_ids = []
	for order in orders:
		customer_name = formatCustomerName(order)
		order_number = order['order_number']
		order_name = order['name']
		order_date = order['created_at']
		status_url = order['order_status_url']

		matching_orders = Order.objects.filter(channel='shopify', number=order_number, team=team).order_by('-created_at')
		if matching_orders.count() > 0:
			new_order = matching_orders.first()
			new_order.status = status
			new_order.customer = customer_name
			new_order.url = status_url
			new_order.name = order_name
			new_order.save()
		else:
			new_order = Order.objects.create(channel='shopify', number=order_number, team=team, name=order_name, created_at=order_date, url=status_url, status=status, customer=customer_name)

		order_ids.append(new_order.id)

		for line_item in order['line_items']:
			variant_id = line_item['variant_id']
			variant_sku = line_item['sku']
			quantity = line_item['quantity']
			matching_skus = ShopifySKU.objects.filter(variant_id=variant_id, team=team, channel='shopify')
			if matching_skus.count() > 0:
				matching_sku = matching_skus.first()
			else:
				main_title = line_item['title']
				variant_title = line_item['variant_title']
				if variant_title != '' or len(variant_title.strip()) > 0:
					main_title = main_title + " - " + variant_title
				matching_sku = ShopifySKU.objects.create(name=main_title, variant_id=variant_id, team=team, channel='shopify', variant_sku=variant_sku)
			new_li = LineItem.objects.get_or_create(order=new_order, shopify_sku=matching_sku, num_units=quantity)

	return order_ids

@api_view(['GET'])
def loadShopifyOrdersIntoPolymer(request):
	team_id = request.query_params.get('team')
	team = Team.objects.get(pk=team_id)

	# get all open orders
	body = shopifyAPIHelper(request, "admin/orders.json")
	open_shopify_orders = body['orders']
	open_order_ids = getOrCreateOrder(open_shopify_orders, 'i', team)

	body = shopifyAPIHelper(request, "admin/orders.json?status=closed")
	closed_shopify_orders = body['orders']
	closed_order_ids = getOrCreateOrder(closed_shopify_orders, 'c', team)

	# maybe delete the cancelled orders instead???
	body = shopifyAPIHelper(request, "admin/orders.json?status=cancelled")
	cancelled_shopify_orders = body['orders']
	cancelled_order_ids = getOrCreateOrder(cancelled_shopify_orders, 'x', team)

	orders = Order.objects.filter(pk__in=open_order_ids)

	serializer = OrderSerializer(orders, many=True)
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



@api_view(['GET'])
def loadSquarespaceOrdersIntoPolymer(request):
	team_id = request.query_params.get('team')
	team = Team.objects.get(pk=team_id)

	# get all open orders
	orders = squarespaceAPIHelper(request, "orders")
	if orders == None:
		serializer = OrderSerializer(Order.objects.none(), many=True)
		return Response(serializer.data)
	for order in orders:
		number = order['orderNumber']
		billing = order['billingAddress']
		customer = billing['firstName'] + " " + billing['lastName']
		status = order['fulfillmentStatus']
		polymer_order, created = Order.objects.get_or_create(channel="squarespace", customer=customer, number=number, team=team)
		if created:
			for line_item in order['lineItems']:
				name = line_item['productName']
				quantity = line_item['quantity']
				sku = line_item['sku']
				sku_id = line_item['productId']
				variants = line_item['variantOptions']
				if len(variants) > 0:
					name += " -- "
				for variant in variants:
					name += variant['value']
				polymer_sku = ShopifySKU.objects.get_or_create(channel="squarespace", team=team, variant_id=sku_id, variant_sku=sku, name=name)
				polymer_lineitem = LineItem.objects.get_or_create(order=polymer_order, shopify_sku=polymer_sku, num_units=quantity)
		# what are the different squarespace order statuses? convert these to i c x
		polymer_order.status = status
		polymer_order.save()

	orders = Order.objects.filter(team=team)
	serializer = OrderSerializer(orders, many=True)
	return Response(serializer.data)


def squarespaceAPIHelper(request, url):
	team_id = request.query_params.get('team')
	team = Team.objects.get(pk=team_id)
	# access_token = "Bearer " + team.squarespace_access_token
	access_token = "Bearer " + "22fa0d6c-622f-4b64-9ea5-00a34f5c8486"
	api_url = "https://api.squarespace.com/1.0/commerce/" + url
	r = requests.get(api_url, headers={"Authorization": access_token})
	results = json.loads(r.text)
	if "result" in results and len(results['result']) > 0:
		return results['result']
	else:
		return None





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


