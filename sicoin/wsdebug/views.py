from django.http import HttpResponse
from django.shortcuts import render

from sicoin.users.tasks import calculate_and_save_incidents_from_resource_statistics


def index(request):
    return render(request, 'wsdebug/index.html')


def incident(request, incident_id):
    return render(request, 'wsdebug/incident.html', {
        'incident_id': incident_id
    })


def run_tasks_sync(request):
    calculate_and_save_incidents_from_resource_statistics()
    return HttpResponse('Tasks ran successfully')
