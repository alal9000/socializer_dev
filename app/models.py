from django.db import models
from django.contrib.auth.models import User

AGE_BAND_CHOICES = [
    ("rather_not_say", "Rather not say"),
    ("under_25", "Under 25"),
    ("25_to_35", "25 - 35"),
    ("36_and_over", "36 and over"),
]


class Profile(models.Model):
    user = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE)
    profile_pic = models.ImageField(default="profile2.png", null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True, null=True)
    description = models.CharField(max_length=500, null=True, blank=True)
    friend_visibility = models.BooleanField(default=True, null=True)
    age_band = models.CharField(
        max_length=20, choices=AGE_BAND_CHOICES, null=True, blank=False, default='rather_not_say'
    )

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"
