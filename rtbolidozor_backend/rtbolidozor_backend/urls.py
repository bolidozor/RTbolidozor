"""rtbolidozor_backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

from . import views


# router = routers.DefaultRouter()
# router.register(r'observatories', views.ObservatoryViewSet)
# router.register(r'stations', views.StationViewSet)
# router.register(r'snapshots/<str:timestamp_str>', views.SnapshotViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('event/', views.realtime_event, name="event"),

    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    path('api/v1/', include('djoser.urls')),
    path('api/v1/', include('djoser.urls.authtoken')),
    path('api/v1/event/', views.realtime_event),
    path('api/v1/observatories/', views.ObservatoryList.as_view()),
    path('api/v1/observatory/<str:identifier>/', views.ObservatoryDetail.as_view()),
    path('api/v1/observatory/<str:identifier>/stations/', views.ObservatoryStations.as_view()),
    path('api/v1/stations/', views.StationList.as_view()),
    path('api/v1/station/<str:identifier>/', views.StationDetail.as_view()),
    path('api/v1/snapshots/<str:timestamp_str>/', views.SnapshotListAtTime.as_view()),
    path('api/v1/multiStationEvent/', views.MultiStationEventViewSet.as_view()),
    path('api/v1/events/', views.EventListView.as_view()),
    path('api/v1/fits/', views.fits_proxy),
    path('api/v1/stats/', views.StatsView.as_view()),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
