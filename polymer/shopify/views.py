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


SHOPIFY_SCOPE = 'read_orders,write_orders'
REDIRECT_URI = 'https://localhost:3000/shopify/ext'

# @csrf_exempt
@api_view(['POST'])
def createShopifyAuthURL(request):
	shop_name = request.POST.get('shopname')
	# shop_name = 'polymerstore'
  # state = ''.join(random.sample('0123456789', 5))
	state = '543234'
	authorization_base_url = "https://" + shop_name + ".myshopify.com/admin/oauth/authorize"

	shopify = OAuth2Session(settings.SHOPIFY_API_KEY, redirect_uri=REDIRECT_URI, scope=SHOPIFY_SCOPE)
	authorization_url, state = shopify.authorization_url(authorization_base_url, state=state)
	print(authorization_url)
	response = HttpResponse(authorization_url, content_type="text/plain")
	return response

# @csrf_exempt
@api_view(['POST'])
def createShopifyAuthToken(request):
	shop_name = request.POST.get('shopname')
  	# shop_name = 'polymerstore'
	token_url = "https://" + shop_name + ".myshopify.com/admin/oauth/access_token"

	auth_response = request.POST.get('auth_response')
	auth_response = auth_response.split("code=",1)[1]
	code = auth_response.split("&",1)[0]

  # user_id = request.POST.get('user_id')
	shopify = OAuth2Session(settings.SHOPIFY_API_KEY,
		redirect_uri=REDIRECT_URI,
		scope=SHOPIFY_SCOPE)
	token = shopify.fetch_token(token_url,
		code=code,
		client_secret=settings.SHOPIFY_SECRET_KEY)
	print(token)
  # save the token to the user
  # success response
	response = HttpResponse(json.dumps({"token": token['access_token']}), content_type="text/plain")
	return response;

def update_userprofile_token(user_profile, token):
	user_profile.gauth_access_token = token['access_token']
	user_profile.gauth_refresh_token = token['refresh_token']
	user_profile.expires_in = token['expires_in']
	user_profile.expires_at = token['expires_at']


# @csrf_exempt
@api_view(['POST'])
def clearToken(request):
	user_id = request.POST.get('user_id')
	user_profile = UserProfile.objects.get(user=user_id)
	user_profile.gauth_access_token = ""
	user_profile.gauth_email = ""
	user_profile.save()
	response = HttpResponse(serializers.serialize('json', [user_profile]))
	return response


