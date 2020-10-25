from django.test import TestCase

from sicoin.domain_config.domain_dict_generator import DomainDictGenerator
from sicoin.domain_config.models import DomainConfig


class TestDomainGenerator(TestCase):
    fixtures = ['sicoin/domain_config/fixtures/data.json']

    def test_domain_generator_returns_dict_successfully(self):
        domain = DomainConfig.objects.get(id=1)
        domain_generator = DomainDictGenerator(domain)
        domain_as_dict = domain_generator.to_dict_representation()

        expected_dict_result = domain.parsed_json
        self.maxDiff = None

        self.assertDictEqual(domain_as_dict, expected_dict_result)
