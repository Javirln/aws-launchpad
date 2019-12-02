from django.conf.urls import url
from django.urls import include

urlpatterns = [
    url(r'^api-auth/', include('rest_framework.urls')),
    url(r'^ec2/', include(('ec2.urls', 'ec2')))
]
