from django.conf.urls import url

from ec2.views import EC2CreateVMView, EC2CheckStatusView, EC2StopInstanceView

urlpatterns = [
    url(r'create', EC2CreateVMView.as_view(), name='create-vm'),
    url(r'check-status', EC2CheckStatusView.as_view(), name='check-status'),
    url(r'stop-instance', EC2StopInstanceView.as_view(), name='stop-instance'),
]
