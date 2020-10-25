from django.test import TestCase
from nose.tools import eq_, ok_
from .serializers import DomainSerializer


class TestCreateDomainSerializer(TestCase):

    def setUp(self):
        self.domain_data = {
            "name": "DominioPersonalizado",
            "supervisorAliases": [
                {
                    "name": "Bombero"
                },
                {
                    "name": "Oficial"
                },
                {
                    "name": "Suboficial"
                }
            ],
            "adminAlias": "Administrador",
            "incidentAbstractions": [
                {
                    "name": "Incidente",
                    "types": [
                        {
                            "name": "Incendio de Campo",
                            "descriptions": [{"text": "descripcion util para un map point en particular"}],
                            "resourceTypes": [{"name": "Bombero"}],
                            "detailsSchema": {}
                        }
                    ]
                },
                {
                    "name": "Búsqueda",
                    "types": [
                        {
                            "name": "Búsqueda",
                            "descriptions": [{"text": "descripcion util para un map point en particular"}],
                            "resourceTypes": [{"name": "Bombero"}, {"name": "Canino"}],
                            "detailsSchema": {}
                        }
                    ]
                }
            ],
            "resourceTypes": [
                {
                    "name": "Bombero"
                },
                {
                    "name": "Canino"
                }
            ]
        }

    def test_serializer_with_empty_data(self):
        serializer = DomainSerializer(data={})
        eq_(serializer.is_valid(), False)

    def test_serializer_with_valid_data(self):
        serializer = DomainSerializer(data=self.domain_data)
        ok_(serializer.is_valid())
        domain = serializer.save()
        eq_(domain.domain_name, 'DominioPersonalizado')
        self.assertIsNotNone(domain.domain_code)

    # TODO: Test w/request and related to user
