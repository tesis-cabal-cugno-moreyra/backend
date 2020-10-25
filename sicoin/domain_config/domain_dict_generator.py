from sicoin.domain_config import models


class DomainDictGenerator:
    def __init__(self, domain: models.DomainConfig):
        self.domain = domain

    def to_dict_representation(self):
        domain_config_as_dict = {
            'name': self.domain.domain_name,
            "supervisorAliases": [self._supervisor_alias_to_dict(alias) for alias in
                                  self.domain.supervisoralias_set.all()],
            "adminAlias": self.domain.admin_alias,
            "incidentAbstractions": [self._incident_abstraction_to_dict(incident) for incident in
                                     self.domain.incidentabstraction_set.all()]
        }
        return domain_config_as_dict

    def _supervisor_alias_to_dict(self, supervisor_alias: models.SupervisorAlias):
        return {
            "name": supervisor_alias.alias
        }

    def _incident_abstraction_to_dict(self, incident_abstraction: models.IncidentAbstraction):
        return {
            "name": incident_abstraction.alias,
            "types": [self._incident_type_to_dict(incident_type) for incident_type in
                      incident_abstraction.incidenttype_set.all()]
        }

    def _incident_type_to_dict(self, incident_type: models.IncidentType):
        return {
            "name": incident_type.name,
            "descriptions": [self._map_point_description_to_dict(map_point) for map_point in
                             incident_type.mappointdescription_set.all()],
            "resourceTypes": [self._incident_type_resource_type_to_dict(resource) for resource in
                              incident_type.incidenttyperesource_set.all()],
            "detailsSchema": incident_type.details_schema
        }

    def _incident_type_resource_type_to_dict(self, incident_type_resource: models.IncidentTypeResource):
        return {
            "name": incident_type_resource.resource_type.name
        }

    def _map_point_description_to_dict(self, map_point_description: models.MapPointDescription):
        return {
            "text": map_point_description.text
        }
