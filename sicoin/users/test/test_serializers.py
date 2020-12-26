from django.test import TestCase
from django.forms.models import model_to_dict
from django.contrib.auth.hashers import check_password
from nose.tools import eq_, ok_
from .factories import UserFactory
from ..serializers import CreateUserSerializer, CreateUpdateSupervisorProfileSerializer, \
    CreateUpdateAdminProfileSerializer, CreateResourceProfileSerializer
from ...domain_config.models import DomainConfig, SupervisorAlias, ResourceType


class TestCreateUserSerializer(TestCase):

    def setUp(self):
        self.user_data = model_to_dict(UserFactory.build())
        self.user_data['domain_code'] = "AABBCCDDEE"
        self.domain = DomainConfig()
        self.domain.domain_name = "Name"
        self.domain.domain_code = "AABBCCDDEE"
        self.domain.parsed_json = {}
        self.domain.save()

    def test_serializer_with_empty_data(self):
        serializer = CreateUserSerializer(data={})
        eq_(serializer.is_valid(), False)

    def test_serializer_with_valid_data(self):
        serializer = CreateUserSerializer(data=self.user_data)
        ok_(serializer.is_valid())

    def test_serializer_hashes_password(self):
        serializer = CreateUserSerializer(data=self.user_data)
        ok_(serializer.is_valid())

        user = serializer.save()
        ok_(check_password(self.user_data.get('password'), user.password))
        eq_(user.is_active, False)


class TestCreateSupervisorProfileSerializer(TestCase):
    def setUp(self):
        self.user = UserFactory.build()
        self.user.save()
        self.domain = DomainConfig()
        self.domain.domain_name = "Name"
        self.domain.domain_code = "AABBCCDDEE"
        self.domain.parsed_json = {}
        self.domain.save()

        self.alias = SupervisorAlias()
        self.alias.alias = "Alias"
        self.alias.domain_config = self.domain
        self.alias.save()

    def test_serializer_with_empty_data(self):
        serializer = CreateUpdateSupervisorProfileSerializer(data={})
        eq_(serializer.is_valid(), False)

    def test_serializer_with_valid_data(self):
        serializer = CreateUpdateSupervisorProfileSerializer(data={
            'domain_code': self.domain.domain_code,
            'domain_name': self.domain.domain_name,
            'user': self.user.id,
            'alias': self.alias.alias,
        })
        eq_(serializer.is_valid(), True)

    def test_serializer_with_non_existent_user(self):
        serializer = CreateUpdateSupervisorProfileSerializer(data={
            'domain_code': self.domain.domain_code,
            'domain_name': self.domain.domain_name,
            'user': '',
            'alias': self.alias.alias,

        })
        eq_(serializer.is_valid(), False)

    def test_serializer_with_invalid_code(self):
        serializer = CreateUpdateSupervisorProfileSerializer(data={
            'domain_code': 'asdasdasd',
            'domain_name': self.domain.domain_name,
            'user': '',
            'alias': self.alias.alias,

        })
        eq_(serializer.is_valid(), False)

    def test_serializer_with_user_with_already_created_profile(self):
        serializer = CreateUpdateSupervisorProfileSerializer(data={
            'domain_code': self.domain.domain_code,
            'domain_name': self.domain.domain_name,
            'user': self.user.id,
            'alias': self.alias.alias,

        })
        eq_(serializer.is_valid(), True)
        serializer.save()

        serializer2 = CreateUpdateSupervisorProfileSerializer(data={
            'domain_code': self.domain.domain_code,
            'domain_name': self.domain.domain_name,
            'user': self.user.id,
            'alias': self.alias.alias,

        })
        eq_(serializer2.is_valid(), False)

    def test_serializer_with_non_existent_domain(self):
        serializer = CreateUpdateSupervisorProfileSerializer(data={
            'domain_code': self.domain.domain_code,
            'domain_name': 'asdasdasd',
            'user': self.user.id,
            'alias': self.alias.alias,

        })
        eq_(serializer.is_valid(), False)

    def test_serializer_with_non_existent_alias(self):
        serializer = CreateUpdateSupervisorProfileSerializer(data={
            'domain_code': self.domain.domain_code,
            'domain_name': self.domain.domain_name,
            'user': self.user.id,
            'alias': 'asdasdasd',

        })
        eq_(serializer.is_valid(), False)


class TestCreateAdminProfileSerializer(TestCase):
    def setUp(self):
        self.user = UserFactory.build()
        self.user.save()
        self.domain = DomainConfig()
        self.domain.domain_name = "Name"
        self.domain.domain_code = "AABBCCDDEE"
        self.domain.admin_alias = "Alias"
        self.domain.parsed_json = {}
        self.domain.save()

    def test_serializer_with_empty_data(self):
        serializer = CreateUpdateAdminProfileSerializer(data={})
        eq_(serializer.is_valid(), False)

    def test_serializer_with_valid_data(self):
        serializer = CreateUpdateAdminProfileSerializer(data={
            'domain_code': self.domain.domain_code,
            'domain_name': self.domain.domain_name,
            'user': self.user.id,
        })
        eq_(serializer.is_valid(), True)

    def test_serializer_with_non_existent_user(self):
        serializer = CreateUpdateAdminProfileSerializer(data={
            'domain_code': self.domain.domain_code,
            'domain_name': self.domain.domain_name,
            'user': '',

        })
        eq_(serializer.is_valid(), False)

    def test_serializer_with_invalid_code(self):
        serializer = CreateUpdateAdminProfileSerializer(data={
            'domain_code': 'asdasdasd',
            'domain_name': self.domain.domain_name,
            'user': '',

        })
        eq_(serializer.is_valid(), False)

    def test_serializer_with_user_with_already_created_profile(self):
        serializer = CreateUpdateAdminProfileSerializer(data={
            'domain_code': self.domain.domain_code,
            'domain_name': self.domain.domain_name,
            'user': self.user.id,

        })
        eq_(serializer.is_valid(), True)
        serializer.save()

        serializer2 = CreateUpdateAdminProfileSerializer(data={
            'domain_code': self.domain.domain_code,
            'domain_name': self.domain.domain_name,
            'user': self.user.id,

        })
        eq_(serializer2.is_valid(), False)

    def test_serializer_with_non_existent_domain(self):
        serializer = CreateUpdateAdminProfileSerializer(data={
            'domain_code': self.domain.domain_code,
            'domain_name': 'asdasdasd',
            'user': self.user.id,

        })
        eq_(serializer.is_valid(), False)


class TestCreateResourceProfileSerializer(TestCase):
    def setUp(self):
        self.user = UserFactory.build()
        self.user.save()
        self.domain = DomainConfig()
        self.domain.domain_name = "Name"
        self.domain.domain_code = "AABBCCDDEE"
        self.domain.parsed_json = {}
        self.domain.save()

        self.type = ResourceType()
        self.type.name = "Type"
        self.type.domain_config = self.domain
        self.type.save()

    def test_serializer_with_empty_data(self):
        serializer = CreateResourceProfileSerializer(data={})
        eq_(serializer.is_valid(), False)

    def test_serializer_with_valid_data(self):
        serializer = CreateResourceProfileSerializer(data={
            'domain_code': self.domain.domain_code,
            'domain_name': self.domain.domain_name,
            'user': self.user.id,
            'type': self.type.name,
        })
        eq_(serializer.is_valid(), True)

    def test_serializer_with_non_existent_user(self):
        serializer = CreateResourceProfileSerializer(data={
            'domain_code': self.domain.domain_code,
            'domain_name': self.domain.domain_name,
            'user': '',
            'type': self.type.name,

        })
        eq_(serializer.is_valid(), False)

    def test_serializer_with_invalid_code(self):
        serializer = CreateResourceProfileSerializer(data={
            'domain_code': 'asdasdasd',
            'domain_name': self.domain.domain_name,
            'user': '',
            'type': self.type.name,

        })
        eq_(serializer.is_valid(), False)

    def test_serializer_with_user_with_already_created_profile(self):
        serializer = CreateResourceProfileSerializer(data={
            'domain_code': self.domain.domain_code,
            'domain_name': self.domain.domain_name,
            'user': self.user.id,
            'type': self.type.name,

        })
        eq_(serializer.is_valid(), True)
        serializer.save()

        serializer2 = CreateResourceProfileSerializer(data={
            'domain_code': self.domain.domain_code,
            'domain_name': self.domain.domain_name,
            'user': self.user.id,
            'type': self.type.name,

        })
        eq_(serializer2.is_valid(), False)

    def test_serializer_with_non_existent_domain(self):
        serializer = CreateResourceProfileSerializer(data={
            'domain_code': self.domain.domain_code,
            'domain_name': 'asdasdasd',
            'user': self.user.id,
            'type': self.type.name,

        })
        eq_(serializer.is_valid(), False)

    def test_serializer_with_non_existent_alias(self):
        serializer = CreateResourceProfileSerializer(data={
            'domain_code': self.domain.domain_code,
            'domain_name': self.domain.domain_name,
            'user': self.user.id,
            'type': 'asdasdasd',

        })
        eq_(serializer.is_valid(), False)
