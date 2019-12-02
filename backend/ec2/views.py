import logging

from core.exceptions import AWSException
from core.services import AmazonService
from django.forms import Form, fields
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

logger = logging.getLogger(__name__)


class EC2VMRequest(Form):
    client_id = fields.CharField(required=True, max_length=128)
    client_secret = fields.CharField(required=True, max_length=128)


class EC2VMStatus(EC2VMRequest):
    instance_id = fields.CharField(required=True, max_length=128)


class EC2StopInstanceView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        request_form = EC2VMStatus(request.data)
        if not request_form.is_valid():
            return Response(data=request_form.errors, status=status.HTTP_400_BAD_REQUEST)

        client_id = request_form.cleaned_data['client_id']
        client_secret = request_form.cleaned_data['client_secret']
        instance_id = request_form.cleaned_data['instance_id']

        try:
            data = AmazonService.stop_instance(instance_id, client_id, client_secret)

            return Response(data)

        except AWSException as aws_e:
            return Response(data=str(aws_e), status=aws_e.status)
        except Exception as e:
            return Response(data=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class EC2CheckStatusView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        request_form = EC2VMStatus(request.data)
        if not request_form.is_valid():
            return Response(data=request_form.errors, status=status.HTTP_400_BAD_REQUEST)

        client_id = request_form.cleaned_data['client_id']
        client_secret = request_form.cleaned_data['client_secret']
        instance_id = request_form.cleaned_data['instance_id']

        try:
            data = AmazonService.get_instance_status(instance_id, client_id, client_secret)

            return Response(data)

        except AWSException as aws_e:
            return Response(data=str(aws_e), status=aws_e.status)
        except Exception as e:
            return Response(data=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class EC2CreateVMView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        request_form = EC2VMRequest(request.data)
        if not request_form.is_valid():
            return Response(data=request_form.errors, status=status.HTTP_400_BAD_REQUEST)

        client_id = request_form.cleaned_data['client_id']
        client_secret = request_form.cleaned_data['client_secret']

        try:
            data = AmazonService.create_vm(client_id, client_secret)
            return Response(data)

        except AWSException as aws_e:
            return Response(data=str(aws_e), status=aws_e.status)
        except Exception as e:
            return Response(data=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
