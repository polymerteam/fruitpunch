# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import csv

from api.models import *
from django.http import HttpResponse
from requests_oauthlib import OAuth2Session, TokenUpdated
from django.conf import settings
from rest_framework.decorators import api_view
import requests
import datetime
import random
import simplejson as json


SHOPIFY_SCOPE = 'read_all_orders,read_orders,write_orders,read_products'
REDIRECT_URI = 'https://localhost:3000/shopify/ext'

# @csrf_exempt
@api_view(['POST'])
def createShopifyAuthURL(request):
	shop_name = request.data['shopname']
	if 'team_id' in request.data:
		team_id = request.data['team_id']
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
	print('!!!!!!!!!!!!!!')
	print(token)
	print('!!!!!!!!!!!!!!')
	if 'team_id' in request.data:
		team_id = request.data['team_id']
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




# @api_view(['POST'])
def getShopifyProducts(request):	
	return shopifyAPIHelper(request, "admin/products.json?fields=id,title,variants")

# @api_view(['POST'])
def getShopifyOrders(request):	
	return shopifyAPIHelper(request, "admin/orders.json")

def shopifyAPIHelper(request, url):
	team_id = request.GET.get('team_id')
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
	response = HttpResponse(json.dumps({"body": body}), content_type="text/plain")
	return response;

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


