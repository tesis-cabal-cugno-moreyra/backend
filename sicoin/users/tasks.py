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


class IncidentTypeStatsFilter:
    def __init__(self, resource_id: int):
        self.resource_id = resource_id
        self.incident_types = IncidentType.objects.all().order_by('name')

    def get_incident_type_names(self):
        return [incident_type.name for incident_type in self.incident_types]

    def get_incident_quantity(self):
        return [Incident.objects.filter(incident_type__name=incident_type.name).count()
                for incident_type in self.incident_types]

    def get_incident_assisted_quantity(self):
        return [Incident.objects.filter(incident_type__name=incident_type.name,
                                        incidentresource__resource_id=self.resource_id).count()
                for incident_type in self.incident_types]


class IncidentStatsByTimeFilter:
    def __init__(self, resource_id: int):
        self.resource_id = resource_id
        self.now = datetime.now()

    def get_week_array_starting_from_weekday(self):
        weekday = self.now.weekday()
        assert 0 <= weekday <= 6, f"Weekday with value {weekday} has to be between 0 and 6"
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
        assert 0 <= today_weekday <= 6, f"Weekday with value {today_weekday} has to be between 0 and 6"
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
        assert 0 <= today_weekday <= 6, f"Weekday with value {today_weekday} has to be between 0 and 6"
        days_of_week = range(0, 7)

        for weekday in list(islice(cycle(days_of_week), today_weekday, 7 + today_weekday)):
            filtered_incidents.append(
                Incident.objects.filter(created_at__week_day=weekday, created_at__range=(a_week_ago, self.now)).count()
            )

        assert len(filtered_incidents) == 7
        return filtered_incidents

    def get_last_6_months_array(self):
        months = [
            "Enero",
            "Febrero",
            "Marzo",
            "Abril",
            "Mayo",
            "Junio",
            "Julio",
            "Agosto",
            "Septiembre",
            "Octubre",
            "Noviembre",
            "Diciembre",
        ]
        return list(islice(cycle(months), self.now.month + 5, self.now.month + 11))

    def get_incidents_assisted_quantity_last_6_months(self):
        incident_quantity_per_month = []
        for month in list(islice(cycle(range(1, 13)), self.now.month + 5, self.now.month + 11)):
            incident_quantity_per_month.append(
                Incident.objects.filter(created_at__month=month, incidentresource__resource_id=self.resource_id).count()
            )
        return incident_quantity_per_month

    def get_incidents_total_quantity_last_6_months(self):
        incident_quantity_per_month = []
        for month in list(islice(cycle(range(1, 13)), self.now.month + 5, self.now.month + 11)):
            incident_quantity_per_month.append(
                Incident.objects.filter(created_at__month=month).count()
            )
        return incident_quantity_per_month

    def get_years_array(self):
        return list(range(Incident.objects.earliest('created_at').created_at.year, self.now.year + 1))

    def get_incidents_assisted_quantity_by_year(self):
        incident_quantity_per_year = []
        for year in range(Incident.objects.earliest('created_at').created_at.year, self.now.year + 1):
            incident_quantity_per_year.append(
                Incident.objects.filter(created_at__year=year, incidentresource__resource_id=self.resource_id).count()
            )

        return incident_quantity_per_year

    def get_incidents_total_quantity_by_year(self):
        incident_quantity_per_year = []
        for year in range(Incident.objects.earliest('created_at').created_at.year, self.now.year + 1):
            incident_quantity_per_year.append(
                Incident.objects.filter(created_at__year=year).count()
            )

        return incident_quantity_per_year


@app.task(bind=True)
def calculate_and_save_incidents_from_resource_statistics(self):
    for resource in ResourceProfile.objects.all():
        incident_type_stats_registry = IncidentTypeStatsFilter(resource_id=resource.id)
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
