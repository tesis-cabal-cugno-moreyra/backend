from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import User, AdminProfile, SupervisorProfile, ResourceProfile
from ..domain_config.models import DomainConfig, SupervisorAlias, ResourceType


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name',)
        read_only_fields = ('username', )


class CreateUserSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        # call create_user on user object. Without this
        # the password will be stored in plain text.
        user = User.objects.create_user(**validated_data)
        user.is_active = False
        return user

    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'first_name', 'last_name', 'email', 'auth_token', 'is_active')
        read_only_fields = ('auth_token', 'is_active')
        extra_kwargs = {'password': {'write_only': True}}


class AdminProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = AdminProfile
        fields = ('id', 'user', 'domain', 'role')
        depth = 1


class CreateAdminProfileSerializer(serializers.ModelSerializer):
    domain = serializers.PrimaryKeyRelatedField(queryset=DomainConfig.objects.all(), required=False)

    class Meta:
        model = AdminProfile
        fields = ('id', 'user', 'domain', 'role')


class SupervisorProfileSerializer(serializers.ModelSerializer):
    domain = serializers.PrimaryKeyRelatedField(queryset=DomainConfig.objects.all(), read_only=False)
    alias = serializers.PrimaryKeyRelatedField(queryset=SupervisorAlias.objects.all(), read_only=False)
    # This should receive domain supervisor as name!

    class Meta:
        model = SupervisorProfile
        fields = ('id', 'user', 'domain', 'alias')


class ResourceProfileSerializer(serializers.ModelSerializer):
    domain = serializers.PrimaryKeyRelatedField(queryset=DomainConfig.objects.all(), read_only=False)
    type = serializers.PrimaryKeyRelatedField(queryset=ResourceType.objects.all(), read_only=False)
    # This should receive domain resource type as name!

    class Meta:
        model = ResourceProfile
        fields = ('id', 'user', 'domain', 'type')


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['first_name'] = user.first_name
        token['last_name'] = user.last_name
        token['email'] = user.email
        roles = []
        try:
            if user.adminprofile.domain:
                roles.append({
                    user.adminprofile.role: user.adminprofile.domain.admin_alias
                })
            else:
                roles.append({
                    user.adminprofile.role: None
                })
        except ObjectDoesNotExist:
            pass  # Log here!
        try:
            roles.append({
                user.supervisorprofile.role: user.supervisorprofile.alias.alias
            })
        except ObjectDoesNotExist:
            pass  # Log here!
        try:
            roles.append({
                user.resourceprofile.role: user.resourceprofile.type.name
            })
        except ObjectDoesNotExist:
            pass  # Log here!

        token['roles'] = roles

        return token
