from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from . import views

urlpatterns = [

    #url(r'^$', views.index, name='index'),
    url(r'^create-auth-url/$', views.createShopifyAuthURL, name='x'),
    url(r'^create-auth-token/$', views.createShopifyAuthToken, name='y'),
    url(r'^get-shopify-products/$', views.getShopifyProducts, name='x'),
    url(r'^get-shopify-orders/$', views.getShopifyOrders, name='x'),
    # url(r'^clear-token/$', views.clearToken, name='b'),


]

urlpatterns = format_suffix_patterns(urlpatterns)