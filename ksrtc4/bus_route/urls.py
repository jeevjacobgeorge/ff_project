from django.urls import path
from . import views

urlpatterns = [
    path('', views.bus_route_view, name='bus_route_view'),
]
