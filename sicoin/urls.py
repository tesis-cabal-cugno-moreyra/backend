import os

from django.conf import settings
from django.urls import path, re_path, include, reverse_lazy
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic.base import RedirectView
from rest_framework.routers import DefaultRouter

from .incident.views import AddIncidentResourceToIncidentAPIView, IncidentCreateListViewSet
from .users import views
from .domain_config.views import DomainConfigAPIView, GenerateNewDomainCodeAPIView,\
    GetCurrentDomainCodeAPIView, CheckCurrentDomainCodeAPIView
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

router = DefaultRouter()
router.register(r'users', views.UserCreateListViewSet)
router.register(r'users', views.UserRetrieveUpdateViewSet)
router.register(r'admins', views.AdminProfileViewSet)
router.register(r'admins', views.AdminProfileCreateViewSet)
router.register(r'supervisors', views.SupervisorProfileViewSet)
router.register(r'supervisors', views.SupervisorProfileCreateUpdateListViewSet)
router.register(r'resources', views.ResourceProfileCreateUpdateViewSet)
router.register(r'resources', views.ResourceProfileRetrieveDestroyViewSet)
router.register(r'incidents', IncidentCreateListViewSet)

schema_view = get_schema_view(
    openapi.Info(
        title="Snippets API",
        default_version='v1',
        description="Test description",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@snippets.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    url=os.getenv('DEFAULT_API_URL', None),
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('chat/', include('chat.urls')),
    path('admin/', admin.site.urls),
    path('api/v1/', include(router.urls)),
    path('api/v1/domain-config/', DomainConfigAPIView.as_view()),
    path('api/v1/domain-config/renew-domain-code/', GenerateNewDomainCodeAPIView.as_view()),
    path('api/v1/domain-config/domain-code/', GetCurrentDomainCodeAPIView.as_view()),
    path('api/v1/domain-config/domain-code/check/', CheckCurrentDomainCodeAPIView.as_view()),
    # path('api/v1/incidents/<int:incident_id>/resources/', ListResourcesFromIncident.as_view()),
    path('api/v1/incidents/<int:incident_id>/resources/<int:resource_id>/',
         AddIncidentResourceToIncidentAPIView.as_view()),

    re_path(r'^rest-auth/', include('dj_rest_auth.urls')),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('hello/', views.HelloView.as_view()),

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
