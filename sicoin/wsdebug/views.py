from django.shortcuts import render


def index(request):
    return render(request, 'wsdebug/index.html')


def incident(request, incident_id):
    return render(request, 'wsdebug/incident.html', {
        'incident_id': incident_id
    })
