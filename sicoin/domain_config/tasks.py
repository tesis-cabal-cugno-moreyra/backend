from datetime import datetime, timezone

import statistics

from sicoin.celery import app
from sicoin.domain_config.models import IncidentType
from sicoin.incident.models import Incident


def get_mean_std_cancelled_incidents_from_type(incident_type):
    cancelled_incidents_tds = []
    for incident in Incident.objects.filter(incident_type=incident_type, status=Incident.INCIDENT_STATUS_CANCELED):
        cancelled_incidents_tds.append((incident.cancelled_at - incident.created_at).total_seconds())
    return statistics.mean(cancelled_incidents_tds), statistics.stdev(cancelled_incidents_tds)


def get_mean_std_finalized_incidents_from_type(incident_type):
    finalized_incidents_tds = []
    for incident in Incident.objects.filter(incident_type=incident_type, status=Incident.INCIDENT_STATUS_FINALIZED):
        finalized_incidents_tds.append((incident.finalized_at - incident.created_at).total_seconds())
    return statistics.mean(finalized_incidents_tds), statistics.stdev(finalized_incidents_tds)


@app.task(bind=True)
def calculate_incident_stats_from_incident_type(self):
    for incident_type in IncidentType.objects.all():
        incident_type.general_stats = {
            'calculatedAt': datetime.utcnow().replace(tzinfo=timezone.utc).isoformat(),
            'averageWorkTimeCancelled': '22h 15m',
            'stdWorkTimeCancelled': '22h 15m',
            'averageWorkTimeFinalized': '',
            'stdWorkTimeFinalized': '',
        }
        incident_type.save(update_fields=['general_stats'])
        print(f"Successfully calculated stats for incident of type {incident_type.name}")
