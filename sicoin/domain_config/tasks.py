from datetime import datetime, timezone

import statistics

from sicoin.celery import app
from sicoin.domain_config.models import IncidentType
from sicoin.incident.models import Incident


def get_mean_std_incidents_by_type_and_status(incident_type, status):
    incidents_total_seconds = []
    for incident in Incident.objects.filter(incident_type=incident_type, status=status):
        incidents_total_seconds.append((incident.finalized_at - incident.created_at).total_seconds())
    if not len(incidents_total_seconds):
        return 0, 0
    if len(incidents_total_seconds) == 1:
        return incidents_total_seconds[0], 0
    return statistics.mean(incidents_total_seconds), statistics.stdev(incidents_total_seconds)


@app.task(bind=True)
def calculate_incident_stats_from_incident_type(self):
    for incident_type in IncidentType.objects.all():
        average_work_time_cancelled, std_work_time_cancelled = get_mean_std_incidents_by_type_and_status(
            incident_type, Incident.INCIDENT_STATUS_CANCELED
        )
        average_work_time_finalized, std_work_time_finalized = get_mean_std_incidents_by_type_and_status(
            incident_type, Incident.INCIDENT_STATUS_FINALIZED
        )
        incident_type.general_stats = {
            'calculatedAt': datetime.utcnow().replace(tzinfo=timezone.utc).isoformat(),
            'averageWorkTimeCancelled': int(average_work_time_cancelled),
            'stdWorkTimeCancelled': int(std_work_time_cancelled),
            'averageWorkTimeFinalized': int(average_work_time_finalized),
            'stdWorkTimeFinalized': int(std_work_time_finalized),
        }
        incident_type.save(update_fields=['general_stats'])
        print(f"Successfully calculated stats for incident of type {incident_type.name}")
