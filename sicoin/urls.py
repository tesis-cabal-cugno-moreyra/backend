from django.conf import settings
from django.urls import path, re_path, include, reverse_lazy
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic.base import RedirectView
from rest_framework.routers import DefaultRouter

from .geolocation.views import GetMapPointsFromIncident, CreateMapPoint, CreateTrackPoint, GetTrackPointsFromIncident, \
    CreateTrackPoints
from .incident.views import AddIncidentResourceToIncidentAPIView, IncidentCreateListViewSet, \
    ValidateIncidentDetailsAPIView, IncidentAssistanceWithExternalSupportAPIView, \
    IncidentAssistanceWithoutExternalSupportAPIView, IncidentStatusFinalizeAPIView, \
    IncidentStatusCancelAPIView, IncidentResourceViewSet, IncidentResourceFromResourceListView
from .users import views
from .domain_config.views import DomainConfigAPIView, GenerateNewDomainCodeAPIView, \
    GetCurrentDomainCodeAPIView, CheckCurrentDomainCodeAPIView, StatisticsByIncidentType
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg.generators import OpenAPISchemaGenerator
from drf_yasg import openapi

from .users.views import ActivateUserView, DeactivateUserView, CreateOrUpdateResourceProfileDeviceData, \
    StatisticsByResource

router = DefaultRouter()
router.register(r'users', views.UserCreateListViewSet)
router.register(r'users', views.UserRetrieveUpdateViewSet)
router.register(r'admins', views.AdminProfileRetrieveUpdateDestroyViewSet)
router.register(r'admins', views.AdminProfileCreateListViewSet)
router.register(r'supervisors', views.SupervisorProfileRetrieveUpdateDestroyViewSet)
router.register(r'supervisors', views.SupervisorProfileCreateUpdateListViewSet)
router.register(r'resources', views.ResourceProfileRetrieveUpdateDestroyViewSet)
router.register(r'resources', views.ResourceProfileCreateRetrieveListViewSet)
router.register(r'incidents/(?P<incident_id>\d+)/resources', IncidentResourceViewSet)
router.register(r'incidents', IncidentCreateListViewSet)


class BothHttpAndHttpsSchemaGenerator(OpenAPISchemaGenerator):
    def get_schema(self, request=None, public=False):
        schema = super().get_schema(request, public)
        schema.schemes = ["http", "https"]
        return schema


schema_view = get_schema_view(
    openapi.Info(
        title="SiCoIn Rest API Documentation!",
        default_version='v1',
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    generator_class=BothHttpAndHttpsSchemaGenerator,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('chat/', include('chat.urls')),
    path('wsdebug/', include('sicoin.wsdebug.urls')),
    path('admin/', admin.site.urls),
    path('api/v1/', include(router.urls)),
    path('api/v1/domain-config/', DomainConfigAPIView.as_view()),
    path('api/v1/domain-config/renew-domain-code/', GenerateNewDomainCodeAPIView.as_view()),
    path('api/v1/domain-config/domain-code/', GetCurrentDomainCodeAPIView.as_view()),
    path('api/v1/domain-config/domain-code/check/', CheckCurrentDomainCodeAPIView.as_view()),
    path('api/v1/incidents/<int:incident_id>/finalize/', IncidentStatusFinalizeAPIView.as_view()),
    path('api/v1/incidents/<int:incident_id>/cancel/', IncidentStatusCancelAPIView.as_view()),
    path('api/v1/incidents/<int:incident_id>/with-external-support/',
         IncidentAssistanceWithExternalSupportAPIView.as_view()),
    path('api/v1/incidents/<int:incident_id>/without-external-support/',
         IncidentAssistanceWithoutExternalSupportAPIView.as_view()),
    path('api/v1/incidents/<int:incident_id>/details/', ValidateIncidentDetailsAPIView.as_view()),
    path('api/v1/incidents/<int:incident_id>/resources/<int:resource_id>/',
         AddIncidentResourceToIncidentAPIView.as_view()),
    path('api/v1/incidents/<int:incident_id>/resources/<int:resource_id>/map-point/',
         CreateMapPoint.as_view()),
    path('api/v1/incidents/<int:incident_id>/map-points/', GetMapPointsFromIncident.as_view()),
    path('api/v1/incidents/<int:incident_id>/resources/<int:resource_id>/track-point/', CreateTrackPoint.as_view()),
    path('api/v1/incidents/<int:incident_id>/resources/<int:resource_id>/track-points/', CreateTrackPoints.as_view()),
    path('api/v1/incidents/<int:incident_id>/track-points/', GetTrackPointsFromIncident.as_view()),

    path('api/v1/incident-types/<str:incident_type_name>/statistics/', StatisticsByIncidentType.as_view()),  # REVISAR

    path('api/v1/resources/<int:resource_id>/create-or-update-device/',
         CreateOrUpdateResourceProfileDeviceData.as_view()),
    path('api/v1/resources/<int:resource_id>/incidents/', IncidentResourceFromResourceListView.as_view()),
    path('api/v1/resources/<int:resource_id>/statistics/', StatisticsByResource.as_view()),

    path('api/v1/users/<uuid:user_id>/activate/', ActivateUserView.as_view()),
    path('api/v1/users/<uuid:user_id>/deactivate/', DeactivateUserView.as_view()),

    re_path(r'^rest-auth/', include('dj_rest_auth.urls')),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('hello/', views.HelloView.as_view()),
    path('logging/', views.LoggingView.as_view()),

    # ^^ FIXME: Separate urls along all apps
    path('api-auth/google-login/', views.GoogleView.as_view()),

    # the 'api-root' from django rest-frameworks default router
    # http://www.django-rest-framework.org/api-guide/routers/#defaultrouter
    re_path(r'^$', RedirectView.as_view(url=reverse_lazy('api-root'), permanent=False)),

    re_path(r'^swagger(?P<format>\.json|\.yaml)$',
            schema_view.without_ui(cache_timeout=0), name='schema-json'),
    re_path(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    re_path(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
