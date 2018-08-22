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

class TeamList(generics.ListCreateAPIView):
  queryset = Team.objects.all()
  serializer_class = TeamSerializer

class TeamGet(generics.RetrieveAPIView):
  queryset = Team.objects.all()
  serializer_class = TeamSerializer

# #######

class ProductList(generics.ListCreateAPIView):
  queryset = Product.objects.all()
  serializer_class = ProductSerializer

class ProductDetail(generics.RetrieveUpdateDestroyAPIView):
  queryset = Product.objects.all()
  serializer_class = ProductSerializer

class ShopifySKUList(generics.ListCreateAPIView):
  queryset = ShopifySKU.objects.all()
  serializer_class = ShopifySKUSerializer

class ShopifySKUDetail(generics.RetrieveUpdateDestroyAPIView):
  queryset = ShopifySKU.objects.all()
  serializer_class = ShopifySKUSerializer

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

    # amount_used = Batch.objects.filter(is_trashed=False, status='c')\
    #     .annotate(ingredient_amount=Sum('active_recipe__ingredients__amount', filter=Q(active_recipe__ingredients__product=OuterRef('pk'))))\
    #     .annotate(recipe_batch_size=F('active_recipe__default_batch_size'))\
    #     .annotate(amt_in_batch=F('amount')*F('ingredient_amount')/F('recipe_batch_size'))\
    #     .order_by().values('amt_in_batch')

    # total_amount_used = amount_used.annotate(total=Sum('amt_in_batch')).values('total')

    queryset = Product.objects.all().annotate(in_progress_amount=Coalesce(Sum('batches__amount', filter=Q(batches__status='i')), 0))
    queryset = queryset.annotate(completed_amount=Coalesce(Sum('batches__amount', filter=Q(batches__status='c')), 0))
    queryset = queryset.annotate(received_amount_total=Coalesce(Sum('received_inventory__amount'), 0))
    # queryset = queryset.annotate(asdf=Subquery(total_amount_used))
    # TODO: we also need to get all the batches which have no active recipe that match this product and subtracted those that are completed


    results = []
    for product in queryset:
      #received amount also needs to subtract the amount that was used as an ingredient to batches that were completed
      # should we also subtract the amount that is being used for in progress batches??
      amount_used = Batch.objects.filter(is_trashed=False, status='c')\
        .annotate(ingredient_amount=Sum('active_recipe__ingredients__amount', filter=Q(active_recipe__ingredients__product=product)))\
        .annotate(recipe_batch_size=F('active_recipe__default_batch_size'))\
        .annotate(amt_in_batch=F('amount')*F('ingredient_amount')/F('recipe_batch_size'))\
        .aggregate(Sum('amt_in_batch'))
      if not amount_used['amt_in_batch__sum']:
        amount_used = 0
      else:
        amount_used = amount_used['amt_in_batch__sum']
      available = product.received_amount_total - amount_used + product.completed_amount
      results.append({'id': product.id, 'in_progress_amount': product.in_progress_amount, 'available_amount': available})

    return results


# >>> newest = Comment.objects.filter(post=OuterRef('pk')).order_by('-created_at')
# >>> Post.objects.annotate(newest_commenter_email=Subquery(newest.values('email')[:1]))


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
