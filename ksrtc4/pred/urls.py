from django.urls import path
from . import views

urlpatterns = [
    path('', views.demand_forecast, name='demand_forecast'),
]
