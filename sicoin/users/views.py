import django_filters
import requests
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.hashers import make_password
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
from .notify_resource_user import notify_resource_user_activation, notify_resource_user_deactivation
from . import serializers
from django.core.cache import cache


class UserRetrieveUpdateViewSet(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer
    permission_classes = (AllowAny,)


class UserCreateListViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = serializers.CreateUserSerializer
    permission_classes = (AllowAny,)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = serializers.UserSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = serializers.UserSerializer(queryset, many=True)
        return Response(serializer.data)


class AdminProfileRetrieveUpdateDestroyViewSet(mixins.RetrieveModelMixin, mixins.UpdateModelMixin,
                                               mixins.DestroyModelMixin, viewsets.GenericViewSet):
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
                                                    mixins.DestroyModelMixin,
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


class ResourceProfileRetrieveUpdateDestroyViewSet(mixins.UpdateModelMixin, mixins.DestroyModelMixin,
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
        if user.is_active and user.resourceprofile:
            notify_resource_user_activation(user.resourceprofile)
        elif not user.is_active and user.resourceprofile:
            notify_resource_user_deactivation(user.resourceprofile)
        elif user.is_active and not user.resourceprofile:
            # Activated user that is NOT a resource
            pass
        elif not user.is_active and not user.resourceprofile:
            # Deactivated user that is NOT a resource
            pass
        else:
            raise Exception(f'User {user} could not be notified')
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

        fcm_device_serializer = FCMDeviceSerializer(data=request.data)
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
