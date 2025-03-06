"""
URL configuration for ksrtc1 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from django.urls import path,include
from passenger_distribution import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.select_month_time, name='select_month_time'),
    # Route for the map generation with the selected month and time
    path('generate-map/', views.generate_bus_stop_map, name='generate_bus_stop_map'),
    path('geocoding-progress/', views.get_geocoding_progress, name='geocoding_progress'),
    path('ask_chatbot/', views.ask_gemini, name='ask_chatbot'),
    path('pred/', include('pred.urls')),
    path('tracker/', include('tracker.urls')),
    path('route/', include('bus_route.urls'))
]
