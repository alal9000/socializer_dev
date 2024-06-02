from django.db import models
from app.models import Profile

# Create your models here.

class Album(models.Model):
  name = models.CharField(max_length=100, null=False, blank=False)

  def __str__(self):
    return self.name

class Photo(models.Model):
  category = models.ForeignKey(Album, on_delete=models.SET_NULL, null=True, blank=True)
  image = models.ImageField(null=False, blank=False)
  description = models.TextField()
  profile = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True)
  timestamp = models.DateTimeField(auto_now_add=True, null=True)


  def __str__(self):
    return self.description


