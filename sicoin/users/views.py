import logging

import django_filters
import requests
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.hashers import make_password
from django.db.models import ProtectedError
from django.http import HttpResponse
from django_filters import rest_framework as filters
from drf_yasg.utils import swagger_auto_schema
from fcm_django.api.rest_framework import FCMDeviceSerializer
from rest_framework import viewsets, mixins, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.utils import json
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User, AdminProfile, ResourceProfile, SupervisorProfile
from .notify_user_manager import UserStatusChangeNotificationManager
from . import serializers
from django.core.cache import cache

from ..incident.models import IncidentResource


class DestroyWitProtectedCatchMixin(mixins.DestroyModelMixin):
    def destroy(self, request, *args, **kwargs):
        try:
            return super().destroy(request, args, kwargs)
        except ProtectedError:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class UserRetrieveUpdateViewSet(mixins.UpdateModelMixin, viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer
    permission_classes = (AllowAny,)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        self.serializer_class = serializers.UserDetailsAfterLoginSerializer
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class UserRetrieveViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = serializers.UserDetailsAfterLoginSerializer
    permission_classes = (AllowAny,)


class UserCreateListViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = serializers.CreateUserSerializer
    permission_classes = (AllowAny,)
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_fields = ('username', 'first_name',
                        'last_name', 'is_active')

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = serializers.UserDetailsAfterLoginSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = serializers.UserDetailsAfterLoginSerializer(queryset, many=True)
        return Response(serializer.data)


class AdminProfileRetrieveUpdateDestroyViewSet(mixins.RetrieveModelMixin, mixins.UpdateModelMixin,
                                               DestroyWitProtectedCatchMixin, viewsets.GenericViewSet):
    queryset = AdminProfile.objects.all()
    serializer_class = serializers.CreateUpdateAdminProfileSerializer
    permission_classes = (AllowAny,)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = serializers.ListRetrieveAdminProfileSerializer(instance)
        return Response(serializer.data)


class AdminProfileCreateListViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = AdminProfile.objects.all()
    serializer_class = serializers.CreateUpdateAdminProfileSerializer
    permission_classes = (AllowAny,)
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_fields = ('user__username', 'user__first_name',
                        'user__last_name', 'user__is_active')

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = serializers.ListRetrieveAdminProfileSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = serializers.ListRetrieveAdminProfileSerializer(queryset, many=True)
        return Response(serializer.data)


class SupervisorProfileRetrieveUpdateDestroyViewSet(mixins.UpdateModelMixin,
                                                    DestroyWitProtectedCatchMixin,
                                                    viewsets.GenericViewSet):
    queryset = SupervisorProfile.objects.all()
    serializer_class = serializers.CreateUpdateSupervisorProfileSerializer
    permission_classes = (AllowAny,)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = serializers.ListRetrieveSupervisorProfileSerializer(instance)
        return Response(serializer.data)


class SupervisorProfileCreateUpdateListViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = SupervisorProfile.objects.all()
    serializer_class = serializers.CreateUpdateSupervisorProfileSerializer
    permission_classes = (AllowAny,)
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_fields = ('user__username', 'user__first_name', 'user__last_name',
                        'user__is_active', 'alias__alias')

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = serializers.ListRetrieveSupervisorProfileSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = serializers.ListRetrieveSupervisorProfileSerializer(queryset, many=True)
        return Response(serializer.data)


class ResourceProfileRetrieveUpdateDestroyViewSet(mixins.UpdateModelMixin, DestroyWitProtectedCatchMixin,
                                                  viewsets.GenericViewSet):
    queryset = ResourceProfile.objects.all()
    serializer_class = serializers.UpdateResourceProfileSerializer
    permission_classes = (AllowAny,)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = serializers.ListRetrieveResourceProfileSerializer(instance)
        return Response(serializer.data)


class ResourceFilter(django_filters.FilterSet):
    user__username = django_filters.CharFilter(lookup_expr='iexact')
    user__first_name = django_filters.CharFilter(lookup_expr='iexact')
    user__last_name = django_filters.CharFilter(lookup_expr='iexact')
    user__is_active = django_filters.CharFilter(lookup_expr='iexact')
    type__name = django_filters.CharFilter(lookup_expr='iexact')
    type__is_able_to_contain_resources = django_filters.BooleanFilter(lookup_expr='isnull')

    class Meta:
        model = ResourceProfile
        exclude = ['user', 'type', 'domain']


class ResourceProfileCreateRetrieveListViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = ResourceProfile.objects.all()
    serializer_class = serializers.CreateResourceProfileSerializer
    permission_classes = (AllowAny,)
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = ResourceFilter

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = serializers.ListRetrieveResourceProfileSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = serializers.ListRetrieveResourceProfileSerializer(queryset, many=True)
        return Response(serializer.data)


class HelloView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request):
        cache.set("key", "Hello from redis cache!", timeout=None)
        content = {'message': cache.get("key")}
        return HttpResponse(json.dumps(content))


class LoggingView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        logging.info(request.data)
        return HttpResponse(json.dumps(request.data))


class ChangeUserStatusUserView(APIView):
    permission_classes = (AllowAny,)

    @swagger_auto_schema(operation_description="Activate or deactivate user, Only Admin user",
                         responses={200: "{'message': 'Changed user status successfully'}",
                                    400: "{'message': 'User id invalid or empty'},"
                                         "{'message': 'Error changing user status'}"})
    def post(self, request, user_id):
        if not user_id:
            return HttpResponse(json.dumps({'message': 'User id invalid or empty'}),
                                status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return HttpResponse(json.dumps({'message': 'Error changing user status'}),
                                status=status.HTTP_400_BAD_REQUEST)

        if user.is_active == self.get_user_is_active_change_to():
            return HttpResponse(json.dumps({'message': 'Error changing user status'}),
                                status=status.HTTP_400_BAD_REQUEST)

        user.is_active = self.get_user_is_active_change_to()
        user_notification_manager = UserStatusChangeNotificationManager(user)
        user_notification_manager.notify_user_status_change()
        user.save()
        return HttpResponse(json.dumps({'message': 'Changed user status successfully'}))

    def get_user_is_active_change_to(self) -> bool:
        raise NotImplementedError()


class ActivateUserView(ChangeUserStatusUserView):
    def get_user_is_active_change_to(self):
        return True


class DeactivateUserView(ChangeUserStatusUserView):
    def get_user_is_active_change_to(self):
        return False


class CreateOrUpdateResourceProfileDeviceData(APIView):
    permission_classes = (AllowAny,)

    @swagger_auto_schema(operation_description="Creates or updates resource profile device data, Only Resource user",
                         request_body=FCMDeviceSerializer,
                         responses={200: "{'message': 'Device data for resource with id {RESOURCE_ID} "
                                         "was saved successfully'}",
                                    400: "{'message': 'Resource id invalid or empty'},"
                                         "{'message': 'Error creating or updating resource device id'}"})
    def post(self, request, resource_id):
        if not resource_id:
            return HttpResponse(json.dumps({'message': 'Resource id invalid or empty'}),
                                status=status.HTTP_400_BAD_REQUEST)

        try:
            resource = ResourceProfile.objects.get(id=resource_id)
        except ResourceProfile.DoesNotExist:
            return HttpResponse(json.dumps({'message': 'Error creating or updating resource device id'}),
                                status=status.HTTP_400_BAD_REQUEST)

        fcm_device_serializer = FCMDeviceSerializer(data=request.data, context={'request': request})
        if fcm_device_serializer.is_valid(raise_exception=True):
            fcm_device_serializer.save()
            resource.device = fcm_device_serializer.instance
            resource.save()
            return HttpResponse(json.dumps({'message': f'Device data for resource with id '
                                                       f'{resource_id} was saved successfully'}),
                                status=status.HTTP_200_OK)


class GoogleView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        r = requests.get('https://oauth2.googleapis.com/tokeninfo?id_token={}'
                         .format(request.data.get("token")))
        data = json.loads(r.text)

        if 'error' in data:
            content = {'message': 'wrong google token / this google token is already expired.'}
            return HttpResponse(json.dumps(content))

        # create user if not exist
        try:
            user = User.objects.get(email=data['email'])
        except User.DoesNotExist:
            user = User()
            user.username = data['email']
            user.password = make_password(BaseUserManager().make_random_password())
            user.email = data['email']
            user.save()

        token = RefreshToken.for_user(user)  # generate token without username & password
        response = {'username': user.username, 'access_token': str(token.access_token),
                    'refresh_token': str(token)}
        return HttpResponse(json.dumps(response))


class StatisticsByResource(APIView):
    permission_classes = (AllowAny,)

    def get(self, request):
        response = {
            "barChartData": {
                "labels": [
                    "Campos",
                    "Estructurales",
                    "Vehículos",
                    "Pastizales",
                    "Rescates",
                    "Accidentes",
                    "Varios"
                ],
                "datasets": [
                    {
                        "label": "Cantidad de Incidentes",
                        "backgroundColor": "red",
                        "barThickness": 25,
                        "maxBarThickness": 35,
                        "data": [40, 39, 10, 40, 39, 80, 40]
                    },
                    {
                        "label": "Cantidad de Incidentes Asistidos",
                        "backgroundColor": "green",
                        "barThickness": 25,
                        "maxBarThickness": 35,
                        "data": [4, 9, 1, 30, 29, 10, 37]
                    }
                ]
            },
            "pieChartData": {
                "labels": [
                    "Campos",
                    "Estructurales",
                    "Vehículos",
                    "Pastizales",
                    "Rescates",
                    "Accidentes",
                    "Varios"
                ],
                "datasets": [
                    {
                        "data": [40, 39, 10, 40, 39, 80, 40],
                        "backgroundColor": [
                            "red",
                            "blue",
                            "yellow",
                            "green",
                            "white",
                            "orange",
                            "purple"
                        ]
                    }
                ]
            },
            "lineChartDataWeekly": {
                "labels": [
                    "Domingo",
                    "Lunes",
                    "Martes",
                    "Miércoles",
                    "Jueves",
                    "Viernes",
                    "Sábado"
                ],
                "datasets": [
                    {
                        "label": "Incidentes asistidos",
                        "data": [1, 2, 0, 1, 0, 0, 1],
                        "borderColor": "green"
                    },
                    {
                        "label": "Total incidentes por día",
                        "data": [4, 9, 1, 3, 9, 1, 3],
                        "borderColor": "red"
                    }
                ]
            },
            "lineChartDataMonthly": {
                "labels": [
                    "Noviembre",
                    "Diciembre",
                    "Enero",
                    "Febrero",
                    "Marzo",
                    "Abril"
                ],
                "datasets": [
                    {
                        "label": "Incidentes asistidos",
                        "data": [14, 25, 22, 13, 12, 7, 10],
                        "borderColor": "green"
                    },
                    {
                        "label": "Total incidentes por mes",
                        "data": [34, 45, 102, 30, 32, 67, 12],
                        "borderColor": "red"
                    }
                ]
            },
            "lineChartDataAnnually": {
                "labels": ["2019", "2020", "2021"],
                "datasets": [
                    {
                        "label": "Incidentes asistidos",
                        "data": [123, 234, 78],
                        "borderColor": "green"
                    },
                    {
                        "label": "Total incidentes por mes",
                        "data": [354, 420, 92],
                        "borderColor": "red"
                    }
                ]
            }
        }
        return HttpResponse(json.dumps(response))
