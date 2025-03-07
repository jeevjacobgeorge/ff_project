from django.contrib import admin
from .models import Route, Schedule, Trip

# Custom admin for Route model
class RouteAdmin(admin.ModelAdmin):
    # Display the fields in the list view of the admin interface
    list_display = ('route_no','order_sequence', 'stop_name', 'stop_latitude', 'stop_longitude', 'fare_stage')
    # Add search functionality to search by route_no and stop_name
    search_fields = ('route_no', 'stop_name')
    # Add a filter for fare_stage to filter based on whether the stop is a fare stage
    list_filter = ('fare_stage',)
    # Order the records by route_no
    ordering = ('route_no',)
    # Make route_no a read-only field (it will be automatically uppercased)
    
# Custom admin for Schedule model
class ScheduleAdmin(admin.ModelAdmin):
    # Display the fields in the list view of the admin interface
    list_display = ('schedule_no', 'trip_no', 'route_no', 'source', 'destination', 'service_type', 'start_time', 'end_time')
    # Add search functionality to search by schedule_no, route_no, source, and destination
    search_fields = ('schedule_no', 'route_no', 'source', 'destination')
    # Add filters for service_type, start_time, and end_time
    list_filter = ('service_type', 'start_time', 'end_time')
    # Order the records by schedule_no, trip_no, and order_sequence
    ordering = ('schedule_no', 'trip_no')
    # Make schedule_no, trip_no, and order_sequence read-only fields

# Custom admin for Trip model
class TripAdmin(admin.ModelAdmin):
    # Display the fields in the list view of the admin interface, including the epkm property
    list_display = ('date', 'schedule_no', 'trip_no', 'revenue', 'distance_km', 'epkm')
    # Add search functionality to search by schedule_no, trip_no, and date
    search_fields = ('schedule_no__schedule_no', 'trip_no', 'date')
    # Add filters for date and schedule_no
    list_filter = ('date', 'schedule_no')
    # Order the records by date, schedule_no, and trip_no
    ordering = ('date', 'schedule_no', 'trip_no')
    # Make schedule_no, trip_no, and date read-only fields

    # Display the epkm property (calculated field) in the admin
    def epkm(self, obj):
        if obj.epkm:
            return f"{obj.epkm:.2f}"  # Format the epkm value to 2 decimal places
        return "N/A"
    epkm.admin_order_field = 'epkm'  # Enable sorting by the epkm field

# Register the models with their respective admin classes
admin.site.register(Route, RouteAdmin)
admin.site.register(Schedule, ScheduleAdmin)
admin.site.register(Trip, TripAdmin)
