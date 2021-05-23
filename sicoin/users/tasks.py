import dataclasses

from sicoin.celery import app
from sicoin.incident.models import Incident
from sicoin.users.models import User


@dataclasses.dataclass()
class IncidentTypeStatsByResource:
    incident_type: str
    incident_quantity: int
    incident_assisted_quantity: int


class IncidentTypeStatsRegistry:
    incident_type_stats = []

    def add_incident_type_stats(self, incident_type: str):
        incident_quantity = Incident.objects.filter(incident_type__name=incident_type).count()



@app.task(bind=True)
def calculate_and_save_incidents_from_resource_statistics(self):
    statistics = {
        "dateCalculated": '',  # Date en UTC
        "barChartData": {
            "labels": [
                "Campos",
                "Estructurales",
                "Vehículos",
                "Pastizales",
                "Rescates",
                "Accidentes",
                "Varios"
            ],
            "datasets": [
                {
                    "label": "Cantidad de Incidentes",
                    "backgroundColor": "red",
                    "barThickness": 25,
                    "maxBarThickness": 35,
                    "data": [40, 39, 10, 40, 39, 80, 40]
                },
                {
                    "label": "Cantidad de Incidentes Asistidos",
                    "backgroundColor": "green",
                    "barThickness": 25,
                    "maxBarThickness": 35,
                    "data": [4, 9, 1, 30, 29, 10, 37]
                }
            ]
        },
        "pieChartData": {
            "labels": [
                "Campos",
                "Estructurales",
                "Vehículos",
                "Pastizales",
                "Rescates",
                "Accidentes",
                "Varios",
                "asdasd",
                "ghfdhfghfg",
            ],
            "datasets": [
                {
                    "data": [4, 9, 1, 30, 29, 10, 37, 55, 12], # Cant de incidentes asistidos
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
            "labels": [
                "Domingo",
                "Lunes",
                "Martes",
                "Miércoles",
                "Jueves",
                "Viernes",
                "Sábado"
            ],
            "datasets": [
                {
                    "label": "Incidentes asistidos",
                    "data": [1, 2, 0, 1, 0, 0, 1],
                    "borderColor": "green"
                },
                {
                    "label": "Total incidentes por día",
                    "data": [4, 9, 1, 3, 9, 1, 3],
                    "borderColor": "red"
                }
            ]
        },
        "lineChartDataMonthly": {
            "labels": [
                "Noviembre",
                "Diciembre",
                "Enero",
                "Febrero",
                "Marzo",
                "Abril"
            ],
            "datasets": [
                {
                    "label": "Incidentes asistidos",
                    "data": [14, 25, 22, 13, 12, 7, 10],
                    "borderColor": "green"
                },
                {
                    "label": "Total incidentes por mes",
                    "data": [34, 45, 102, 30, 32, 67, 12],
                    "borderColor": "red"
                }
            ]
        },
        "lineChartDataAnnually": {
            "labels": ["2019", "2020", "2021"],
            "datasets": [
                {
                    "label": "Incidentes asistidos",
                    "data": [123, 234, 78],
                    "borderColor": "green"
                },
                {
                    "label": "Total incidentes por mes",
                    "data": [354, 420, 92],
                    "borderColor": "red"
                }
            ]
        }
    }
    # Cantidad de incidentes en los que participó total. (Texto)
    # IncidentResource.objects.get(resource__pk=resource_pk) ()
    # Cantidad de incidentes en los que participó por tipo. (RadarChart)
    # IncidentResource.objects.get(resource__pk=resource_pk) ->
    # result = [{
    #     'type': 'Campos', ''
    # }]
    # Cantidad de incidentes por mes, por día y por año (LineChart o BarChart)
    #
    # Tiempo promedio de trabajo en cada tipo de incidente (Barchart)
    #
    # 3 tipos de incidente más frecuente a los que asistió (PieChart, 4 colores)
    #
    # Comparativa de tiempo de trabajo por incidente (últimos 10 incidentes, BarChart)
    #
    # Listado de incidentes en los que participó (card con link, tabla)

    print('Start')
