from django.urls import path
from . import views
from .views import get_route_details

urlpatterns = [
    path('', views.bus_route_view, name='bus_route_view'),
    path('get-route-details/', get_route_details, name='get_route_details'),

]
