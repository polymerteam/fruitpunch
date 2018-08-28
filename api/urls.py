from django.conf.urls import url, include
from rest_framework.urlpatterns import format_suffix_patterns



urlpatterns = [ 
    url(r'^v1/', include('api.v1.urls')),
    url(r'', include('api.v1.urls'))
]

urlpatterns = format_suffix_patterns(urlpatterns)