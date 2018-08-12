from rest_framework.response import Response
from rest_framework import generics
from api.v1.serializers import *
import django_filters
from rest_framework.filters import OrderingFilter
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from api.paginations import *
import datetime
from django.http import HttpResponse, HttpResponseForbidden
import pytz
import json
from rest_framework.decorators import api_view
from django.conf import settings


class UserList(generics.ListAPIView):
  queryset = User.objects.all()
  serializer_class = UserSerializer

class UserGet(generics.RetrieveAPIView):
  queryset = User.objects.all()
  serializer_class = UserSerializer

# #######

class ProductList(generics.ListCreateAPIView):
  queryset = Product.objects.all()
  serializer_class = ProductSerializer

class ProductDetail(generics.RetrieveUpdateDestroyAPIView):
  queryset = Product.objects.all()
  serializer_class = ProductSerializer

class RecipeList(generics.ListCreateAPIView):
  queryset = Recipe.objects.all()
  serializer_class = RecipeSerializer

class RecipeDetail(generics.RetrieveUpdateDestroyAPIView):
  queryset = Recipe.objects.all()
  serializer_class = RecipeSerializer

class IngredientList(generics.ListCreateAPIView):
  queryset = Ingredient.objects.all()
  serializer_class = IngredientSerializer

class IngredientDetail(generics.RetrieveUpdateDestroyAPIView):
  queryset = Ingredient.objects.all()
  serializer_class = IngredientSerializer

# class UserProfileList(generics.ListAPIView):
#   queryset = UserProfile.objects.all()
#   serializer_class = UserProfileSerializer

# # userprofiles/[pk]/
# class UserProfileGet(generics.RetrieveAPIView):
#   queryset = UserProfile.objects.all()
#   serializer_class = UserProfileSerializer

# class ProcessList(generics.ListCreateAPIView):
#   serializer_class = ProcessTypeWithUserSerializer
#   filter_backends = (OrderingFilter, DjangoFilterBackend)
#   filter_fields = ('created_by', 'team_created_by', 'id')

#   def get_queryset(self):
#     return process_search(self.request.query_params)

#   def get(self, request):
#     queryset = self.filter_queryset(self.get_queryset())
#     serializer = self.serializer_class(queryset, many=True)
#     ordering = request.query_params.get('ordering', '')
#     reverse = ordering[0:1] == '-'
#     field = ordering[1:] if reverse else ordering
#     if field == 'last_used':
#       data = sorted(serializer.data, key=lambda p: p['last_used'], reverse=reverse)
#     else:
#       data = serializer.data
#     return Response(data)


# # processes/[pk]/ ...where pk = 'primary key' == 'the id'
# class ProcessDetail(generics.RetrieveUpdateDestroyAPIView):
#   queryset = ProcessType.objects.all()\
#     .select_related('created_by', 'team_created_by')\
#     .prefetch_related('attribute_set')
#   serializer_class = ProcessTypeWithUserSerializer
