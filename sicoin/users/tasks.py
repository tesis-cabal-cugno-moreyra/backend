import dataclasses
from datetime import datetime, timedelta, timezone
from itertools import islice, cycle

from sicoin.celery import app
from sicoin.domain_config.models import IncidentType
from sicoin.incident.models import Incident
from sicoin.users.models import ResourceProfile


@dataclasses.dataclass()
class IncidentTypeStatsByResource:
    incident_type: str
    incident_quantity: int
    incident_assisted_quantity: int


class IncidentTypeStatsFilterRegistry:
    def __init__(self, resource_id: int):
        self.resource_id = resource_id

    incident_type_stats = []

    def add_incident_type_stats(self, incident_type: str):
        self.incident_type_stats.append(
            IncidentTypeStatsByResource(
                incident_type=incident_type,
                incident_quantity=Incident.objects.filter(incident_type__name=incident_type).count(),
                incident_assisted_quantity=Incident.objects.filter(incident_type__name=incident_type,
                                                                   incidentresource__resource_id=self.resource_id
                                                                   ).count()
            )
        )

    def get_incident_type_names(self):
        return [incident_type_stat.incident_type for incident_type_stat in self.incident_type_stats]

    def get_incident_quantity(self):
        return [incident_type_stat.incident_quantity for incident_type_stat in self.incident_type_stats]

    def get_incident_assisted_quantity(self):
        return [incident_type_stat.incident_assisted_quantity for incident_type_stat in self.incident_type_stats]


class IncidentStatsByTimeFilter:
    def __init__(self, resource_id: int):
        self.resource_id = resource_id
        self.now = datetime.now()

    def get_week_array_starting_from_weekday(self):
        weekday = self.now.weekday()
        assert 0 >= weekday >= 6, f"Weekday has to be between 0 and 6"
        days_of_week = [
            "Lunes",
            "Martes",
            "Miércoles",
            "Jueves",
            "Viernes",
            "Sábado",
            "Domingo"
        ]
        return list(islice(cycle(days_of_week), weekday, 7 + weekday))

    def get_incidents_assisted_quantity_last_week_by_day(self):
        a_week_ago = self.now - timedelta(days=7)
        today_weekday = self.now.weekday()
        assert 0 >= today_weekday >= 6, f"Weekday has to be between 0 and 6"
        days_of_week = range(0, 7)

        filtered_incidents = []
        for weekday in list(islice(cycle(days_of_week), today_weekday, 7 + today_weekday)):
            filtered_incidents.append(
                Incident.objects.filter(created_at__week_day=weekday,
                                        created_at__range=(a_week_ago, self.now),
                                        incidentresource__resource_id=self.resource_id
                                        ).count()
            )

        assert len(filtered_incidents) == 7
        return filtered_incidents
    
    def get_incidents_total_quantity_last_week_by_day(self):
        filtered_incidents = []

        a_week_ago = self.now - timedelta(days=7)
        today_weekday = self.now.weekday()
        assert 0 >= today_weekday >= 6, f"Weekday has to be between 0 and 6"
        days_of_week = range(0, 7)

        for weekday in list(islice(cycle(days_of_week), today_weekday, 7 + today_weekday)):
            filtered_incidents.append(
                Incident.objects.filter(created_at__week_day=weekday, created_at__range=(a_week_ago, self.now)).count()
            )

        assert len(filtered_incidents) == 7
        return filtered_incidents

    def get_last_6_months_array(self):
        return [  # Last 6 months
            "Noviembre",
            "Diciembre",
            "Enero",
            "Febrero",
            "Marzo",
            "Abril"
        ]

    def get_incidents_assisted_quantity_last_6_months(self):
        pass

    def get_incidents_total_quantity_last_6_months(self):
        pass

    def get_years_array(self):
        return ["2019", "2020", "2021"]

    def get_incidents_assisted_quantity_by_year(self):
        pass

    def get_incidents_total_quantity_by_year(self):
        pass


@app.task(bind=True)
def calculate_and_save_incidents_from_resource_statistics(self):
    for resource in ResourceProfile.objects.all():
        incident_type_stats_registry = IncidentTypeStatsFilterRegistry(resource_id=resource.id)
        for incident_type in IncidentType.objects.all():
            incident_type_stats_registry.add_incident_type_stats(incident_type=incident_type.name)
    
        incident_by_time_stats_registry = IncidentStatsByTimeFilter(resource_id=resource.id)
     
        resource.stats_by_incident = {
            "calculatedAt": datetime.utcnow().replace(tzinfo=timezone.utc).isoformat(),
            "barChartData": {
                "labels": incident_type_stats_registry.get_incident_type_names(),
                "datasets": [
                    {
                        "label": "Cantidad de Incidentes",
                        "backgroundColor": "red",
                        "barThickness": 25,
                        "maxBarThickness": 35,
                        "data": incident_type_stats_registry.get_incident_quantity()
                    },
                    {
                        "label": "Cantidad de Incidentes Asistidos",
                        "backgroundColor": "green",
                        "barThickness": 25,
                        "maxBarThickness": 35,
                        "data": incident_type_stats_registry.get_incident_assisted_quantity()
                    }
                ]
            },
            "pieChartData": {
                "labels": incident_type_stats_registry.get_incident_type_names(),
                "datasets": [
                    {
                        "data": incident_type_stats_registry.get_incident_assisted_quantity(),
                        "backgroundColor": [
                            "red",
                            "blue",
                            "yellow",
                            "green",
                            "white",
                            "orange",
                            "purple",
                            "aquamarine",
                            "chocolate",
                            "gold",
                            "black",
                            "gray",
                            "ivory",
                            "indigo",
                            "navy",
                            "pink",
                            "violet",
                            "tomato",
                            "teal",
                            "turquoise"
                        ]
                    }
                ]
            },
            "lineChartDataWeekly": {
                "labels": incident_by_time_stats_registry.get_week_array_starting_from_weekday(),
                "datasets": [
                    {
                        "label": "Incidentes asistidos",
                        "data": incident_by_time_stats_registry.get_incidents_assisted_quantity_last_week_by_day(),
                        "borderColor": "green"
                    },
                    {
                        "label": "Total incidentes por día",
                        "data": incident_by_time_stats_registry.get_incidents_total_quantity_last_week_by_day(),
                        "borderColor": "red"
                    }
                ]
            },
            "lineChartDataMonthly": {
                "labels": incident_by_time_stats_registry.get_last_6_months_array(),
                "datasets": [
                    {
                        "label": "Incidentes asistidos",
                        "data": incident_by_time_stats_registry.get_incidents_assisted_quantity_last_6_months(),
                        "borderColor": "green"
                    },
                    {
                        "label": "Total incidentes por mes",
                        "data": incident_by_time_stats_registry.get_incidents_total_quantity_last_6_months(),
                        "borderColor": "red"
                    }
                ]
            },
            "lineChartDataAnnually": {
                "labels": incident_by_time_stats_registry.get_years_array(),
                "datasets": [
                    {
                        "label": "Incidentes asistidos",
                        "data": incident_by_time_stats_registry.get_incidents_assisted_quantity_by_year(),
                        "borderColor": "green"
                    },
                    {
                        "label": "Total incidentes por mes",
                        "data": incident_by_time_stats_registry.get_incidents_total_quantity_by_year(),
                        "borderColor": "red"
                    }
                ]
            }
        }

        resource.save(update_fields=['stats_by_incident'])
        print(f'Saved statistics for resource {resource}')
