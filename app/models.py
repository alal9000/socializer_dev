from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
  user = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE)
  profile_pic = models.ImageField(default="profile2.png", null=True, blank=True)
  date_created = models.DateTimeField(auto_now_add=True, null=True)
  description = models.CharField(max_length=500, null=True, blank=True)

  def __str__(self):
    return f"{self.user}"




