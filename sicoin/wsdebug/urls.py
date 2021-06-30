from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('run-tasks/', views.run_tasks_sync, name='run-tasks-sync'),
    path('<int:incident_id>/', views.incident, name='incident'),
]
