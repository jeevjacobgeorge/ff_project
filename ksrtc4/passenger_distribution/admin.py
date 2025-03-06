# Register your models here.
from django.contrib import admin
from .models import KsrtcFromData, KsrtcToData

# Register the KsrtcFromData model
@admin.register(KsrtcFromData)
class KsrtcFromDataAdmin(admin.ModelAdmin):
    list_display = ('date_hour', 'from_stop_name', 'total_passenger')
    search_fields = ('date_hour', 'from_stop_name')
    list_filter = ('date_hour',)

# Register the KsrtcToData model
@admin.register(KsrtcToData)
class KsrtcToDataAdmin(admin.ModelAdmin):
    list_display = ('date_hour', 'to_stop_name', 'total_passenger')
    search_fields = ('date_hour', 'to_stop_name')
    list_filter = ('date_hour',)
