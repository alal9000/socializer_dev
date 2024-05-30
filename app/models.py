from django.db import models
from django.utils import timezone
from multiselectfield import MultiSelectField
from django.contrib.auth.models import User

# Create your models here.

class Profile(models.Model):
  user = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE)
  profile_pic = models.ImageField(default="profile2.png", null=True, blank=True)
  date_created = models.DateTimeField(auto_now_add=True, null=True)
  description = models.CharField(max_length=500, null=True, blank=True)
  

  def __str__(self):
    return f"{self.user}"

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

  def __str__(self):
      return self.event_title


class Comment(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    comment = models.TextField()

    def __str__(self):
        return f"{self.comment}"


class Message(models.Model):
    receiver = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="messaging")
    message = models.TextField()
    sender = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="messager")
    timestamp = models.DateTimeField()
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.sender} -> {self.receiver}"



