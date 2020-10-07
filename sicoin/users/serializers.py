from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import User, AdminProfile, SupervisorProfile, ResourceProfile
from ..domain_config.models import DomainConfig, SupervisorAlias, ResourceType


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'is_active')
        read_only_fields = ('username', )


class CreateUserSerializer(serializers.ModelSerializer):
    domain_code = serializers.CharField(write_only=True)

    def create(self, validated_data):
        # call create_user on user object. Without this
        # the password will be stored in plain text.
        user = User.objects.create_user(**validated_data)
        user.is_active = False
        return user

    def validate(self, attrs):
        attrs.pop('domain_code', None)
        return super().validate(attrs)

    def validate_domain_code(self, value):
        try:
            domain = DomainConfig.objects.all()[0]
        except IndexError:
            raise serializers.ValidationError("Domain not loaded yet")

        if domain.domain_code != value:
            raise serializers.ValidationError("Invalid code")
        return value

    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'first_name', 'last_name', 'email', 'auth_token', 'is_active',
                  'domain_code')
        read_only_fields = ('auth_token', 'is_active')
        extra_kwargs = {'password': {'write_only': True}}


class AdminProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = AdminProfile
        fields = ('id', 'user', 'domain', 'role')
        depth = 1


class CreateUpdateAdminProfileSerializer(serializers.Serializer):
    domain_code = serializers.CharField(max_length=255)
    user = serializers.UUIDField(read_only=False)
    domain_name = serializers.CharField(max_length=255)

    def validate(self, data):
        try:
            user = User.objects.get(id=data.get('user'))
        except User.DoesNotExist:
            raise serializers.ValidationError(f"User with id {data.get('user')} does not exist")

        try:
            domain = DomainConfig.objects.get(domain_name=data.get('domain_name'))
        except DomainConfig.DoesNotExist:
            raise serializers.ValidationError(f"Domain {data.get('domain_name')} does not exist")

        if domain.domain_code != data.get('domain_code'):
            raise serializers.ValidationError("Invalid code")

        try:
            already_created_profile = AdminProfile.objects.get(user=user)
        except AdminProfile.DoesNotExist:
            already_created_profile = None
        if already_created_profile:
            raise serializers.ValidationError(f"Admin Profile for user with id "
                                              f"{data.get('user')} already exists")

        return data

    def create(self, validated_data):
        admin_profile = AdminProfile(
            user_id=validated_data.get('user'),
            domain=DomainConfig.objects.get(domain_name=validated_data.get('domain_name'))
        )
        admin_profile.save()
        return admin_profile

    def to_representation(self, instance: AdminProfile):
        return {
            'id': instance.id,
            'user': instance.user.id,
            'domain': instance.domain.domain_name,
        }

    class Meta:
        fields = ('id', 'user', 'domain_name', 'alias', 'domain_code')


class CreateUpdateSupervisorProfileSerializer(serializers.Serializer):
    domain_code = serializers.CharField(max_length=255)
    user = serializers.UUIDField(read_only=False)
    domain_name = serializers.CharField(max_length=255)
    alias = serializers.CharField(max_length=255)

    def validate(self, data):
        try:
            user = User.objects.get(id=data.get('user'))
        except User.DoesNotExist:
            raise serializers.ValidationError(f"User with id {data.get('user')} does not exists")

        try:
            already_created_profile = SupervisorProfile.objects.get(user=user)
        except SupervisorProfile.DoesNotExist:
            already_created_profile = None
        if already_created_profile:
            raise serializers.ValidationError(f"Supervisor Profile for user with id "
                                              f"{data.get('user')} already exists")

        try:
            domain = DomainConfig.objects.get(domain_name=data.get('domain_name'))
        except DomainConfig.DoesNotExist:
            raise serializers.ValidationError(f"Domain {data.get('domain_name')} does not exists")

        if domain.domain_code != data.get('domain_code'):
            raise serializers.ValidationError("Invalid code")

        try:
            SupervisorAlias.objects.get(alias__iexact=data.get('alias'),
                                        domain_config__domain_name=data.get('domain_name'))
        except SupervisorAlias.DoesNotExist:
            raise serializers.ValidationError(f"SupervisorAlias {data.get('alias')} for domain "
                                              f"{data.get('domain_name')} does not exists")

        return data

    def create(self, validated_data):
        supervisor_profile = SupervisorProfile(
            user_id=validated_data.get('user'),
            domain=DomainConfig.objects.get(domain_name=validated_data.get('domain_name')),
            alias=SupervisorAlias.objects.get(alias__iexact=validated_data['alias'],
                                              domain_config__domain_name=validated_data['domain_name'])
        )
        supervisor_profile.save()
        return supervisor_profile

    def to_representation(self, instance: SupervisorProfile):
        return {
            'id': instance.id,
            'user': instance.user.id,
            'domain': instance.domain.domain_name,
            'alias': instance.alias.alias
        }

    class Meta:
        fields = ('id', 'user', 'domain_name', 'alias', 'domain_code')


class ListRetrieveSupervisorProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupervisorProfile
        fields = ('id', 'user', 'domain', 'alias')
        depth = 1


class CreateResourceProfileSerializer(serializers.ModelSerializer):
    domain = serializers.PrimaryKeyRelatedField(queryset=DomainConfig.objects.all(), read_only=False)
    type = serializers.CharField(max_length=255)

    def create(self, validated_data):
        # This should receive domain resource type as name!
        supervisor_profile = ResourceProfile(
            user=validated_data['user'],
            domain=validated_data['domain']
        )
        supervisor_profile.alias = SupervisorAlias.objects.get(alias__iexact=validated_data['alias'],
                                                               domain=validated_data['domain'])
        supervisor_profile.save()
        return supervisor_profile

    class Meta:
        model = ResourceProfile
        fields = ('id', 'user', 'domain', 'type')


class ResourceProfileSerializer(serializers.ModelSerializer):
    domain = serializers.PrimaryKeyRelatedField(queryset=DomainConfig.objects.all(), read_only=False)
    type = serializers.PrimaryKeyRelatedField(queryset=ResourceType.objects.all(), read_only=False)

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
