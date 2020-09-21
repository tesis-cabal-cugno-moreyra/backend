import json
import os

from django.http import HttpResponse
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from sicoin.domain_config import models
from sicoin.domain_config.serializers import DomainSerializer
from sicoin.domain_config.utils import get_random_alphanumeric_string


class DomainConfigAPIView(APIView):
    permission_classes = (AllowAny,)

    @swagger_auto_schema(responses={200: DomainSerializer(), 404: 'not found'})
    def get(self, request):
        if len(models.DomainConfig.objects.all()):
            domain_config = models.DomainConfig.objects.all()[0]
            return HttpResponse(json.dumps(domain_config.parsed_json))
        return HttpResponse(json.dumps({'message': 'No Domain exists'}), status=status.HTTP_404_NOT_FOUND)
        # ^^ We currently support a single domain.

    @swagger_auto_schema(operation_description="Creation of domain config. Only Admin user",
                         request_body=DomainSerializer,
                         responses={200: 'Domain successfully created',
                                    400: 'Domain already created'})
    def post(self, request):
        serializer = DomainSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            if len(models.DomainConfig.objects.all()):
                return HttpResponse(json.dumps({'message': 'Another domain is already created.'}),
                                    status=status.HTTP_400_BAD_REQUEST)
                # ^^ We currently support a single domain.

            if bool(os.getenv('SAVE_DOMAIN_CONFIG')):
                serializer.save()
            # ENABLE THIS when frontend trials are finished
            return HttpResponse(json.dumps({'message': 'Domain successfully created'}))


class GenerateNewDomainCodeAPIView(APIView):
    permission_classes = (AllowAny,)

    @swagger_auto_schema(operation_description="Generation of domain code. Only Admin user",
                         responses={200: "{'domain_code': 'NEW_CODE'}",
                                    404: "{'message': 'No Domain exists'}"})
    def get(self, request):
        if len(models.DomainConfig.objects.all()):
            domain_config = models.DomainConfig.objects.all()[0]
            new_domain_code = get_random_alphanumeric_string(10)
            domain_config.domain_code = new_domain_code
            domain_config.save()
            return HttpResponse(json.dumps({'domain_code': domain_config.domain_code}))
        return HttpResponse(json.dumps({'message': 'No Domain exists'}), status=status.HTTP_404_NOT_FOUND)
        # ^^ We currently support a single domain.


class GetCurrentDomainCodeAPIView(APIView):
    permission_classes = (AllowAny,)

    @swagger_auto_schema(operation_description="Retrieval of current domain code. Only Admin user",
                         responses={200: "{'domain_code': 'CURRENT_CODE'}",
                                    404: "{'message': 'No Domain exists'}"})
    def get(self, request):
        if len(models.DomainConfig.objects.all()):
            domain_config = models.DomainConfig.objects.all()[0]
            return HttpResponse(json.dumps({'domain_code': domain_config.domain_code}))
        return HttpResponse(json.dumps({'message': 'No Domain exists'}), status=status.HTTP_404_NOT_FOUND)
        # ^^ We currently support a single domain.
