from django.urls import path
from . import views

urlpatterns = [
    path('index/', views.index, name='index'),  # Keep the index route
    path('staff_login/', views.staff_login, name='staff_login'), 
    path('staff_signup/', views.staff_signup, name='staff_signup'), 
    path('staff_profile/', views.staff_profile, name='staff_profile'),
    path('staff_info/', views.staff_info, name='staff_info'), 
    path('user_main/', views.user_main, name='user_main'),
    path('user_map/', views.user_map, name='user_map'),
]
