from django.db import models
from app.models import Profile

class Event(models.Model):

  event_title = models.CharField(max_length=300)
  total_attendees = models.IntegerField(null=True, blank=True)
  location = models.CharField(max_length=300, null=True, blank=True)
  latitude = models.FloatField(null=True, blank=True)
  longitude = models.FloatField(null=True, blank=True)
  event_date = models.DateField(verbose_name="Event Date", null=True, blank=False)
  event_time = models.TimeField(verbose_name="Time Date", null=True, blank=False)
  description = models.TextField()
  host = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True, blank=True)
  date_created = models.DateTimeField(auto_now_add=True, blank=True)
  guests = models.ManyToManyField(Profile, related_name='attended_events', blank=True)
  cancelled = models.BooleanField(default=False)

  def __str__(self):
      return self.event_title


class Comment(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    comment = models.TextField()

    def __str__(self):
        return f"{self.comment}"
