from django.conf.urls import url
from api.v1 import views


urlpatterns = [
    # url(r'^users/$', views.UserList.as_view()),
    # url(r'^users/(?P<pk>[0-9]+)/$', views.UserGet.as_view()),
    url(r'^teams/$', views.TeamList.as_view()),
    url(r'^teams/(?P<pk>[0-9]+)/$', views.TeamGet.as_view()),

    url(r'^users/create/$', views.UserProfileCreate.as_view()),
    url(r'^userprofiles/$', views.UserProfileList.as_view()),
    url(r'^userprofiles/(?P<pk>[0-9]+)/$', views.UserProfileDetail.as_view()),

    url(r'^products/$', views.ProductList.as_view()),
    url(r'^products/(?P<pk>[0-9]+)/$', views.ProductDetail.as_view()),
    url(r'^products/bulk/$', views.BulkProductCreate.as_view()),

    url(r'^shopify-skus/$', views.ShopifySKUList.as_view()),
    url(r'^shopify-skus/(?P<pk>[0-9]+)/$', views.ShopifySKUDetail.as_view()),

    url(r'^recipes/$', views.RecipeList.as_view()),
    url(r'^recipes/create-with-ingredients/$', views.RecipeCreateWithIngredients.as_view()),
    url(r'^recipes/(?P<pk>[0-9]+)/$', views.RecipeDetail.as_view()),

    url(r'^ingredients/$', views.IngredientList.as_view()),
    url(r'^ingredients/(?P<pk>[0-9]+)/$', views.IngredientDetail.as_view()),

    url(r'^batches/$', views.BatchList.as_view()),
    url(r'^batches/(?P<pk>[0-9]+)/$', views.BatchDetail.as_view()),
    # url(r'^batches/create-with-items/$', views.BatchCreateWithItems.as_view()),

    url(r'^inventories/$', views.InventoryList.as_view()),

    url(r'^received/$', views.ReceivedInventoryList.as_view()),
    url(r'^received/(?P<pk>[0-9]+)/$', views.ReceivedInventoryDetail.as_view()),

    url(r'^orders/$', views.OrderList.as_view()),
    url(r'^orders/(?P<pk>[0-9]+)/$', views.OrderDetail.as_view()),
    url(r'^orders/create-with-items/$', views.OrderCreateWithLineItems.as_view()),

    url(r'^ingredients-in-batches/$', views.getIngredientsForBatches),

    # create product and match sku endpoint - takes in a shopifysku id and information to create a new product

    # url(r'^orders-by-product/$', views.OrdersByProductList.as_view()),

]

