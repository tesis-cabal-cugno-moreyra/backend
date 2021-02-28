from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('<int:incident_id>/', views.incident, name='incident'),
]
