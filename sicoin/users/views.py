import requests
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.hashers import make_password
from django.http import HttpResponse
from rest_framework import viewsets, mixins
from rest_framework.permissions import AllowAny
from rest_framework.utils import json
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User
from .permissions import IsUserOrReadOnly
from .serializers import CreateUserSerializer, UserSerializer
from django.core.cache import cache


class UserViewSet(mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  viewsets.GenericViewSet):
    """
    Updates and retrieves user accounts
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsUserOrReadOnly,)


class UserCreateViewSet(mixins.CreateModelMixin,
                        viewsets.GenericViewSet):
    """
    Creates user accounts
    """
    queryset = User.objects.all()
    serializer_class = CreateUserSerializer
    permission_classes = (AllowAny,)


class HelloView(APIView):
    permission_classes = (AllowAny,)
    def get(self, request):
        cache.set("key", "valueASD", timeout=None)
        content = {'message': cache.get("key")}
        return HttpResponse(json.dumps(content))


class GoogleView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        r = requests.get('https://oauth2.googleapis.com/tokeninfo?id_token={}'.format(request.data.get("token")))
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
        response = {'username': user.username, 'access_token': str(token.access_token), 'refresh_token': str(token)}
        return HttpResponse(json.dumps(response))