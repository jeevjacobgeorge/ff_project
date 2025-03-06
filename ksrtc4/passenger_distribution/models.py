from django.db import models

class KsrtcFromData(models.Model):
    date_hour = models.CharField(max_length=50)
    from_stop_name = models.CharField(max_length=100)
    total_passenger = models.IntegerField()

    def __str__(self):
        return f"{self.date_hour} - {self.from_stop_name}: {self.total_passenger}"

class KsrtcToData(models.Model):
    date_hour = models.CharField(max_length=50)
    to_stop_name = models.CharField(max_length=100)
    total_passenger = models.IntegerField()

    def __str__(self):
        return f"{self.date_hour} - {self.to_stop_name}: {self.total_passenger}"
