from django.db import models
from app.models import Profile

# Create your models here.
class Friend(models.Model):
    sender = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True, related_name="sender")
    receiver = models.ForeignKey(Profile,  on_delete=models.CASCADE, null=True, related_name="receiver")
    status = models.CharField(max_length=10, null=True, choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('denied', 'Denied')], default='pending')

    def __str__(self):
        return f"{self.sender} -> {self.receiver}"
