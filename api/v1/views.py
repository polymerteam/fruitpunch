from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from api.v1.serializers import *
from shopify.serializers import *
import django_filters
from rest_framework.filters import OrderingFilter
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from api.paginations import *
from api import constants
from datetime import datetime
from django.http import HttpResponse, HttpResponseForbidden
import pytz
import json
from rest_framework.decorators import api_view
from django.conf import settings
from django.db.models import OuterRef, Subquery, Q
from django.db.models.functions import Coalesce
from rest_framework.decorators import api_view
from django.contrib.postgres.aggregates.general import ArrayAgg
from django.db.models import Value
from django.db.models.functions import Concat

def teamFilter(queryset, self):
  team = self.request.query_params.get('team', None)
  if team is not None:
    return queryset.filter(team=team)
  else:
    return queryset

class UserList(generics.ListAPIView):
  queryset = User.objects.all()
  serializer_class = UserSerializer


class UserGet(generics.RetrieveAPIView):
  queryset = User.objects.all()
  serializer_class = UserSerializer


class TeamList(generics.ListCreateAPIView):
  queryset = Team.objects.all()
  serializer_class = TeamSerializer


class TeamGet(generics.RetrieveUpdateDestroyAPIView):
  queryset = Team.objects.all()
  serializer_class = TeamSerializer


class UserProfileCreate(generics.CreateAPIView):
  queryset = UserProfile.objects.all()
  serializer_class = UserProfileCreateSerializer


class UserProfileList(generics.ListAPIView):
  queryset = UserProfile.objects.all()
  serializer_class = UserProfileSerializer

  def get_queryset(self):
    queryset = UserProfile.objects.all()
    return teamFilter(queryset, self)

class UserProfileDetail(generics.RetrieveUpdateDestroyAPIView):
  queryset = UserProfile.objects.all()
  serializer_class = UserProfileSerializer


# #######

class ProductList(generics.ListCreateAPIView):
  queryset = Product.objects.all()
  serializer_class = ProductSerializer

  def get_queryset(self):
    queryset = Product.objects.all()
    category = self.request.query_params.get('category', None)
    if category is not None:
      queryset = queryset.filter(category=category)
    return teamFilter(queryset, self)

class ProductDetail(generics.RetrieveUpdateDestroyAPIView):
  queryset = Product.objects.all()
  serializer_class = ProductDetailSerializer


class ShopifySKUList(generics.ListCreateAPIView):
  queryset = ShopifySKU.objects.all()
  serializer_class = ShopifySKUSerializer

  def get_queryset(self):
    queryset = ShopifySKU.objects.all()
    channel = self.request.query_params.get('channel', None)
    if channel is not None:
      queryset = queryset.filter(channel=channel)
    return teamFilter(queryset, self)


class ShopifySKUDetail(generics.RetrieveUpdateDestroyAPIView):
  queryset = ShopifySKU.objects.all()
  serializer_class = ShopifySKUSerializer


class RecipeList(generics.ListCreateAPIView):
  queryset = Recipe.objects.all()
  serializer_class = RecipeSerializer

  def get_queryset(self):
    queryset = Recipe.objects.all()
    team = self.request.query_params.get('team', None)
    if team is not None:
      queryset = queryset.filter(product__team=team)
    return queryset

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

  def get_queryset(self):
    team = self.request.query_params.get('team', None)
    queryset = Ingredient.objects.all()
    if team is not None:
      queryset = queryset.filter(product__team=team)
    return queryset

class IngredientDetail(generics.RetrieveUpdateDestroyAPIView):
  queryset = Ingredient.objects.all()
  serializer_class = IngredientSerializer

class BatchList(generics.ListCreateAPIView):
  # queryset = Batch.objects.all()
  serializer_class = BatchSerializer

  def get_queryset(self):
    queryset = Batch.objects.all()
    team = self.request.query_params.get('team', None)
    if team is not None:
      queryset = queryset.filter(product__team=team)

    start = self.request.query_params.get('start', None)
    end = self.request.query_params.get('end', None)
    if start is not None and end is not None:
      dt = datetime
      start_date = pytz.utc.localize(dt.strptime(start, constants.DATE_FORMAT))
      end_date = pytz.utc.localize(dt.strptime(end, constants.DATE_FORMAT))
      queryset = queryset.filter(started_at__range=(start_date, end_date))

    product_types = self.request.query_params.get('product_types')
    if product_types is not None:
      product_types = product_types.strip().split(',')
      queryset = queryset.filter(product__in=product_types)

    # filter by status (i = in progress, c = completed)
    status_types = self.request.query_params.get('status_types', None)
    if status_types is not None:
      status_types = status_types.strip().split(',')
      queryset = queryset.filter(status__in=status_types)

    queryset = queryset.order_by('started_at')

    return queryset


class BatchDetail(generics.RetrieveUpdateDestroyAPIView):
  queryset = Batch.objects.all()
  serializer_class = BatchSerializer


def annotateProductWithInventory(queryset):
  queryset = queryset.annotate(in_progress_amount=Coalesce(Sum('batches__amount', filter=Q(batches__status='i')), 0))
  queryset = queryset.annotate(completed_amount=Coalesce(Sum('batches__amount', filter=Q(batches__status='c')), 0))
  queryset = queryset.annotate(received_amount_total=Coalesce(Sum('received_inventory__amount'), 0))
  return queryset

def amountUsedOfProduct(product_id):
  amount_used = Batch.objects.filter(is_trashed=False, status='c')\
    .annotate(ingredient_amount=Sum('active_recipe__ingredients__amount', filter=Q(active_recipe__ingredients__product__id=product_id)))\
    .annotate(recipe_batch_size=F('active_recipe__default_batch_size'))\
    .annotate(amt_in_batch=F('amount')*F('ingredient_amount')/F('recipe_batch_size'))\
    .aggregate(Sum('amt_in_batch'))
  if not amount_used['amt_in_batch__sum']:
    amount_used = 0
  else:
    amount_used = amount_used['amt_in_batch__sum']
  return amount_used

class InventoryList(generics.ListAPIView):
  serializer_class = InventorySerializer

  def get_queryset(self):
    team = self.request.query_params.get('team', None)
    if team is None:
      # raise error
      return
    queryset = Product.objects.filter(team=team)

    product_types = self.request.query_params.get('product_types')
    if product_types is not None:
      product_types = product_types.strip().split(',')
      queryset = queryset.filter(id__in=product_types)

    category_types = self.request.query_params.get('category_types')
    if category_types is not None:
      category_types = category_types.strip().split(',')
      queryset = queryset.filter(category__in=category_types)

    queryset = annotateProductWithInventory(queryset)
    # TODO: we also need to get all the batches which have no active recipe that match this product and subtracted those that are completed

    results = []
    for product in queryset:
      #received amount also needs to subtract the amount that was used as an ingredient to batches that were completed
      # should we also subtract the amount that is being used for in progress batches??
      amount_used = amountUsedOfProduct(product.id)
      available = product.received_amount_total - amount_used + product.completed_amount
      results.append({'id': product.id, 'in_progress_amount': product.in_progress_amount, 'available_amount': available})

    return results


class ProductHistory(generics.ListAPIView):
  serializer_class = ProductHistorySerializer

  def get_queryset(self):
    team = self.request.query_params.get('team', None)
    product = self.request.query_params.get('product', None)
    if team is None:
      # raise error
      return
    if product is None:
      # raise error?? or what does this look like for all products???
      return

    timeline = []
    
    # get all the finished batches for creating this product in order
    # TODO: change to completed_at
    created_amounts = Batch.objects.filter(product__team=team, product=product, status='c').order_by('started_at').values_list('started_at', 'amount')
    for obj in created_amounts:
      if obj[1] != None and obj[1] != 0:
        timeline.append({'date': obj[0], 'amount': obj[1], 'message': "created"})
    # get all the received/adjusted inventory for this product in order
    received_or_adjusted_amounts = ReceivedInventory.objects.filter(product=product).order_by('received_at').values_list('received_at', 'amount', 'message')
    for obj in received_or_adjusted_amounts:
      if obj[1] != None and obj[1] != 0:
        timeline.append({'date': obj[0], 'amount': obj[1], 'message': obj[2]})

    # get all the batches for using this product in order
    used_amounts = Batch.objects.filter(is_trashed=False, status='c')\
      .annotate(ingredient_amount=Sum('active_recipe__ingredients__amount', filter=Q(active_recipe__ingredients__product=product)))\
      .annotate(recipe_batch_size=F('active_recipe__default_batch_size'))\
      .annotate(amt_in_batch=F('amount')*F('ingredient_amount')/F('recipe_batch_size'))\
      .values_list('started_at', 'amt_in_batch')
      # TODO: change to completed_at instead of started_at
    for obj in used_amounts:
      if obj[1] != None and obj[1] != 0:
        timeline.append({'date': obj[0], 'amount': obj[1], 'message': 'used as an ingredient'})

    # get all the currently ongoing batches for this product and get the total amount for that
    ongoing_amount = Batch.objects.filter(product=product, status='i').aggregate(Sum('amount'))['amount__sum']
    if ongoing_amount != None and ongoing_amount != 0:
      timeline.append({'date': datetime.now(), 'amount': ongoing_amount, 'message': 'currently in progress being created'})

    # get all the currently ongoing batches that are using this product as a ingredient
    currently_in_use = Batch.objects.filter(is_trashed=False, status='i')\
      .annotate(ingredient_amount=Sum('active_recipe__ingredients__amount', filter=Q(active_recipe__ingredients__product=product)))\
      .annotate(recipe_batch_size=F('active_recipe__default_batch_size'))\
      .annotate(amt_in_batch=F('amount')*F('ingredient_amount')/F('recipe_batch_size'))\
      .aggregate(Sum('amt_in_batch'))['amt_in_batch__sum']

    if currently_in_use != None and currently_in_use != 0:
      timeline.append({'date': datetime.now(), 'amount': currently_in_use, 'message': 'currently in progress being used'})


    timeline.sort(key=lambda x: convert_date(x['date']), reverse=True)

    return [{'product': product, 'timeline': timeline}]

def convert_date(d):
  utc=pytz.UTC
  if d.tzinfo is None or d.tzinfo.utcoffset(d) is None:
    return utc.localize(d)
  else:
    return d

class BulkProductCreate(generics.CreateAPIView):
  queryset = Product.objects.all()
  serializer_class = ProductSerializer

  def create(self, request, *args, **kwargs):
    product_list = request.data['products']
    team = request.data['team']
    for product in product_list:
      product['team'] = int(team)
    serializer = self.get_serializer(data=product_list, many=True)
    if serializer.is_valid():
      serializer.save()
      headers = self.get_success_headers(serializer.data)
      return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 


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

  def get_queryset(self):
    team = self.request.query_params.get('team', None)
    queryset = ReceivedInventory.objects.all()
    if team is not None:
      queryset = queryset.filter(product__team=team)
    return queryset

class ReceivedInventoryDetail(generics.RetrieveUpdateDestroyAPIView):
  queryset = ReceivedInventory.objects.all()
  serializer_class = ReceivedInventorySerializer


class OrderList(generics.ListCreateAPIView):
  queryset = Order.objects.all()
  serializer_class = OrderSerializer

  def get_queryset(self):
    queryset = Order.objects.all()

    queryset = teamFilter(queryset, self)

    start = self.request.query_params.get('start', None)
    end = self.request.query_params.get('end', None)
    if start is not None and end is not None:
      dt = datetime
      start_date = pytz.utc.localize(dt.strptime(start, constants.DATE_FORMAT))
      end_date = pytz.utc.localize(dt.strptime(end, constants.DATE_FORMAT))
      queryset = queryset.filter(created_at__range=(start_date, end_date))

    # filter by status (i = in progress, c = completed, x = cancelled)
    status_types = self.request.query_params.get('status_types', None)
    if status_types is not None:
      status_types = status_types.strip().split(',')
      queryset = queryset.filter(status__in=status_types)

    channel_types = self.request.query_params.get('channel_types', None)
    if channel_types is not None:
      channel_types = channel_types.strip().split(',')
      queryset = queryset.filter(channel__in=channel_types)

    keywords = self.request.query_params.get('keywords', None)
    if keywords is not None:
      queryset = queryset.filter(Q(name__icontains=keywords) | Q(customer__icontains=keywords))

    queryset = queryset.order_by('created_at')

    return queryset




class OrderByProductList(generics.ListAPIView):
  queryset = Order.objects.all()
  serializer_class = ShopifyOrderSerializer

  def get_queryset(self):
    queryset = Order.objects.all()

    status = self.request.query_params.get('status', None)
    channel = self.request.query_params.get('channel', None)
    if status is not None:
      queryset = queryset.filter(status=status)
    if channel is not None:
      queryset = queryset.filter(channel=channel)

    queryset = teamFilter(queryset, self)

    order_map = {}
    customer_map = {}
    for order in queryset:
      for line_item in order.line_items.all():
        if line_item.product == None and line_item.shopify_sku == None:
          continue
        if line_item.product != None:
          product_id = line_item.product.id
          amount = line_item.amount
        elif line_item.shopify_sku != None:
          shopify_sku = line_item.shopify_sku
          product_id = None
          amount = None
          if line_item.shopify_sku.product:
            product_id = line_item.shopify_sku.product.id
            amount = line_item.shopify_sku.conversion_factor * line_item.num_units
        if product_id != None:
          if product_id in order_map:
            order_map[product_id] += amount
          else:
            order_map[product_id] = amount
            customer_map[product_id] = []
          if order.customer and order.customer != "":
            customer_map[product_id].append(order.customer)

    order_list = []
    for obj in order_map:
      order_list.append({'product_id': obj, 'total_amount': order_map[obj], 'customer_name_list': customer_map[obj]})

    return order_list





#     return queryset



class OrderDetail(generics.RetrieveUpdateDestroyAPIView):
  queryset = Order.objects.all()
  serializer_class = OrderSerializer


# this takes in basic order information, and a list of products for lineitems and their amounts
# request data:
# status: i
# name: maya's order
# channel: manual
# created_at: 
# due_date: 
# url: 
# default_batch_size: 2.5
# line_items_data: [{"product":"2","amount":"0.5"},{"product":"3","amount":"2"}]
class OrderCreateWithLineItems(generics.ListCreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderCreateWithLineItemsSerializer


@api_view(['GET'])
def getIngredientsForBatches(request):
  team_id = request.query_params.get('team')
  team = Team.objects.get(pk=team_id)
  # batches = Batch.objects.filter(status='i', product__team=team)
  ingredient_amount_map = {}

  b = Batch.objects.filter(status='i', product__team=team)\
    .annotate(ingredients_list=ArrayAgg(Concat(F('active_recipe__ingredients__product__id'), 
      Value('|'), 
      ExpressionWrapper(F('amount')*F('active_recipe__ingredients__amount')/F('active_recipe__default_batch_size'), output_field=DecimalField()), 
      output_field=CharField())))
  
  # for each batch, add the ingredient amount to it's spot in the ingredient amount map
  ingredient_amount_map = {}
  for x in b:
    ingredients = x.ingredients_list
    for ing in ingredients:
      parts = ing.split('|')
      product_id = int(parts[0])
      amount = float(parts[1])
      if product_id in ingredient_amount_map:
        ingredient_amount_map[product_id] += amount
      else:
        ingredient_amount_map[product_id] = amount

  ing_list = []
  for obj in ingredient_amount_map:
    qs = annotateProductWithInventory(Product.objects.filter(pk=obj))
    amount_used = amountUsedOfProduct(obj)
    inventory_amount = qs[0].received_amount_total - amount_used + qs[0].completed_amount
    ing_list.append({'product_id': obj, 'amount_needed': ingredient_amount_map[obj], 'amount_in_inventory': inventory_amount})

  serializer = IngredientAmountSerializer(ing_list, many=True)
  return Response(serializer.data)


def addProductAmountHelper(item, ingredient_amount_map):
  product = item.id
  amt = item.total_amount
  matching_recipes = Recipe.objects.filter(is_trashed=False, product=product).order_by('-created_at')
  if matching_recipes.count() > 0:
    matching_recipe = matching_recipes.first()
    recipe_size = matching_recipe.default_batch_size
    ingredients = Ingredient.objects.filter(recipe=matching_recipe, is_trashed=False)
    # for each product, get the amounts of the ingredients that are needed to make it
    for ingredient in ingredients:
      added_amt = (ingredient.amount/recipe_size)*amt
      if ingredient.product.id in ingredient_amount_map:
        ingredient_amount_map[ingredient.product.id] += added_amt
      else:
        ingredient_amount_map[ingredient.product.id] = added_amt
  else:
    if product not in ingredient_amount_map:
      ingredient_amount_map[product] = amt
    else:
      ingredient_amount_map[product] += amt

@api_view(['GET'])
def getIngredientsForOrders(request):
  # TODO - add a filter to get the ingredients for orders from a particular channel
  # get all the amounts required for each product from unfulfilled orders
  team_id = request.query_params.get('team')
  team = Team.objects.get(pk=team_id)
  # get the products from the order line items which use shopify skus
  orders_by_product = Product.objects.filter(shopify_skus__line_items__order__status='i', team=team)\
    .annotate(total_num_units=Sum('shopify_skus__line_items__num_units', filter=Q(shopify_skus__line_items__order__status='i')))\
    .annotate(conversion_factors=Avg('shopify_skus__conversion_factor', filter=Q(shopify_skus__line_items__order__status='i')))\
    .annotate(total_amount=ExpressionWrapper(F('total_num_units')*F('conversion_factors'), output_field=DecimalField()))

  # get the products from the order line items which use products directly
  orders_by_product_manual = Product.objects.filter(line_items__order__status='i', team=team)\
    .annotate(total_num_units=Sum('line_items__amount', filter=Q(line_items__order__status='i')))\
    .annotate(total_amount=ExpressionWrapper(F('total_num_units'), output_field=DecimalField()))

  ingredient_amount_map = {}
  for item in orders_by_product:
    addProductAmountHelper(item, ingredient_amount_map)

  for item in orders_by_product_manual:
    addProductAmountHelper(item, ingredient_amount_map)

  ing_list = []
  # for each needed ingredient, annotate it with how much of it is currently in inventory
  for obj in ingredient_amount_map:   
    qs = annotateProductWithInventory(Product.objects.filter(pk=obj))
    amount_used = amountUsedOfProduct(obj)
    inventory_amount = qs[0].received_amount_total - amount_used + qs[0].completed_amount
    ing_list.append({'product_id': obj, 'amount_needed': ingredient_amount_map[obj], 'amount_in_inventory': inventory_amount})

  serializer = IngredientAmountSerializer(ing_list, many=True)
  return Response(serializer.data)
