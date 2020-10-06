import requests
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.hashers import make_password
from django.http import HttpResponse
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, mixins, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.utils import json
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User, AdminProfile, ResourceProfile, SupervisorProfile
from .permissions import IsUserOrReadOnly
from .serializers import CreateUserSerializer, UserSerializer, AdminProfileSerializer, \
    ResourceProfileSerializer, CreateUpdateSupervisorProfileSerializer, CreateAdminProfileSerializer, \
    ListRetrieveSupervisorProfileSerializer
from django.core.cache import cache


class UserRetrieveUpdateViewSet(mixins.RetrieveModelMixin,
                                mixins.UpdateModelMixin,
                                viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsUserOrReadOnly,)


class UserCreateListViewSet(mixins.CreateModelMixin,
                            mixins.ListModelMixin,
                            viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = CreateUserSerializer
    permission_classes = (AllowAny,)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = UserSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = UserSerializer(queryset, many=True)
        return Response(serializer.data)


class AdminProfileViewSet(mixins.RetrieveModelMixin,
                          mixins.UpdateModelMixin,
                          mixins.DestroyModelMixin,
                          viewsets.GenericViewSet):
    queryset = AdminProfile.objects.all()
    serializer_class = AdminProfileSerializer
    permission_classes = (AllowAny,)


class AdminProfileCreateViewSet(mixins.CreateModelMixin,
                                mixins.ListModelMixin,
                                viewsets.GenericViewSet):
    queryset = AdminProfile.objects.all()
    serializer_class = CreateAdminProfileSerializer
    permission_classes = (AllowAny,)

    # def list(self, request, *args, **kwargs):
    #     queryset = self.filter_queryset(self.get_queryset())
    #
    #     page = self.paginate_queryset(queryset)
    #     if page is not None:
    #         serializer = ListRetrieveAdminProfileSerializer(page, many=True)
    #         return self.get_paginated_response(serializer.data)
    #
    #     serializer = ListRetrieveAdminProfileSerializer(queryset, many=True)
    #     return Response(serializer.data)


class SupervisorProfileViewSet(mixins.RetrieveModelMixin,
                               mixins.UpdateModelMixin,
                               mixins.DestroyModelMixin,
                               viewsets.GenericViewSet):
    queryset = SupervisorProfile.objects.all()
    serializer_class = ListRetrieveSupervisorProfileSerializer
    permission_classes = (AllowAny,)


class SupervisorProfileCreateUpdateListViewSet(mixins.CreateModelMixin,
                                               viewsets.GenericViewSet):
    queryset = SupervisorProfile.objects.all()
    serializer_class = CreateUpdateSupervisorProfileSerializer
    permission_classes = (AllowAny,)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ListRetrieveSupervisorProfileSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = ListRetrieveSupervisorProfileSerializer(queryset, many=True)
        return Response(serializer.data)


class ResourceProfileRetrieveDestroyViewSet(mixins.RetrieveModelMixin,
                                            mixins.DestroyModelMixin,
                                            viewsets.GenericViewSet):
    queryset = ResourceProfile.objects.all()
    serializer_class = ResourceProfileSerializer
    permission_classes = (AllowAny,)


class ResourceProfileCreateUpdateViewSet(mixins.CreateModelMixin,
                                         mixins.UpdateModelMixin,
                                         viewsets.GenericViewSet):
    queryset = ResourceProfile.objects.all()
    serializer_class = ResourceProfileSerializer
    permission_classes = (AllowAny,)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ListRetrieveSupervisorProfileSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = ListRetrieveSupervisorProfileSerializer(queryset, many=True)
        return Response(serializer.data)


class HelloView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request):
        cache.set("key", "Hello from redis cache!", timeout=None)
        content = {'message': cache.get("key")}
        return HttpResponse(json.dumps(content))


@swagger_auto_schema(operation_description="Enable user, Only Admin user",
                     request_body={'user_id': 'USER_ID'},
                     responses={200: 'Domain successfully created',
                                400: 'Domain already created'})
class EnableUserView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        user_id = request.data.get('user_id')

        if not user_id:
            return HttpResponse(json.dumps({'message': 'User id invalid or empty'}),
                                status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return HttpResponse(json.dumps({'message': 'Error changing user status'}),
                                status=status.HTTP_400_BAD_REQUEST)

        if user.is_active:
            return HttpResponse(json.dumps({'message': 'Error changing user status'}),
                                status=status.HTTP_400_BAD_REQUEST)

        user.is_active = True
        return HttpResponse(json.dumps({'message': 'User activated successfully'}))


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
