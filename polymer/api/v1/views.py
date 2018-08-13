from rest_framework.response import Response
from rest_framework import status
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
from django.db.models import OuterRef, Subquery
from django.db.models.functions import Coalesce


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


# this takes in a product to define a recipe in, the recipe batch size, and a list of products used as ingredients and their amounts
# request data:
# product_id: 6
# default_batch_size: 2.5
# ingredients_data: [{"product":"2","amount":"0.5"},{"product":"3","amount":"2"}]
class RecipeCreateWithIngredients(generics.ListCreateAPIView):
    queryset = Recipe.objects.all()
    serializer_class = RecipeCreateWithIngredientsSerializer

class RecipeDetail(generics.RetrieveUpdateDestroyAPIView):
  queryset = Recipe.objects.all()
  serializer_class = RecipeSerializer

class IngredientList(generics.ListCreateAPIView):
  queryset = Ingredient.objects.all()
  serializer_class = IngredientSerializer

class IngredientDetail(generics.RetrieveUpdateDestroyAPIView):
  queryset = Ingredient.objects.all()
  serializer_class = IngredientSerializer

class BatchList(generics.ListCreateAPIView):
  # queryset = Batch.objects.all()
  serializer_class = BatchSerializer

  def get_queryset(self):
    queryset = Batch.objects.all()

    # filter by status (i = in progress, c = completed)
    status = self.request.query_params.get('status', None)
    if status is not None:
      queryset = queryset.filter(status=status)

    return queryset


class BatchDetail(generics.RetrieveUpdateDestroyAPIView):
  queryset = Batch.objects.all()
  serializer_class = BatchSerializer


class InventoryList(generics.ListAPIView):
  serializer_class = InventorySerializer

  def get_queryset(self):
    queryset = Product.objects.all().annotate(in_progress_amount=Coalesce(Sum('batches__amount', filter=Q(batches__status='i')), 0))
    queryset = queryset.annotate(completed_amount=Coalesce(Sum('batches__amount', filter=Q(batches__status='c')), 0))
    queryset = queryset.annotate(received_amount_total=Coalesce(Sum('received_inventory__amount'), 0))
    queryset = queryset.annotate(received_amount=F('received_amount_total')-F('in_progress_amount')-F('completed_amount'))
    queryset = queryset.annotate(asdf=F('id'))






    # queryset = queryset.annotate(asdf=Sum(F('batches__amount')*F('batches__active_recipe__ingredients__amount')/F('batches__active_recipe__default_batch_size'), filter=Q(batches__active_recipe__ingredients__product__id__contains=F('id'))))

    # x = Ingredient.objects.filter(product=OuterRef('pk')).order_by().values('product')
    # total_product_as_ingredient = x.annotate(amt=Sum(F('amount')/F(''))).values('amt')


    # x = Batch.objects.filter(active_recipe__ingredients__product__id__contains=OuterRef('pk')).order_by().values('active_recipe__ingredients__product__id')
    # total_product_as_ingredient = x.annotate(amt=Sum(F('amount')*F(''))).values('amt')

    # queryset = queryset.annotate(asdf=Subquery(total_product_as_ingredient))

    # TODO: received amount also needs to subtract the amount that is being used as an ingredient to something else in progress/completed
    queryset = queryset.values('id', 'in_progress_amount', 'completed_amount', 'received_amount', 'asdf')
    return queryset


# takes in data of the format:
# received: [{"product_id": 2, "amount": 2.3}, {"product_id": 4, "amount": 6}]
# {"received": [{"product_id": 2, "amount": 2.3}, {"product_id": 4, "amount": 6}]}
# so you can submit as many received items as you want at the same time and it will create them all
class ReceivedInventoryList(generics.ListCreateAPIView):
  queryset = ReceivedInventory.objects.all()
  serializer_class = ReceivedInventorySerializer

  def create(self, request, *args, **kwargs):
        listofReceived = request.data['received']

        serializer = self.get_serializer(data=listofReceived, many=True)
        if serializer.is_valid():
            serializer.save()
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED,
                            headers=headers)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ReceivedInventoryDetail(generics.RetrieveUpdateDestroyAPIView):
  queryset = ReceivedInventory.objects.all()
  serializer_class = ReceivedInventorySerializer

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
