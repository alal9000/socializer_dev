from django.db import models
from app.models import Profile

class Message(models.Model):
    receiver = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="messaging")
    message = models.TextField()
    sender = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="messager")
    timestamp = models.DateTimeField()

    def __str__(self):
        return f"{self.sender}"
