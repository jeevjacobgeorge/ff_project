from django.urls import path
from . import views
from .views import get_route_details

urlpatterns = [
    path('', views.bus_route_view, name='bus_route_view'),
    path('get-route-details/stops', get_route_details, name='get_route_details'),
    path('get-route-details/schedule', views.bus_route_by_schedule_view, name='get_schedule_details'),

]
