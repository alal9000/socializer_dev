from django.contrib import admin
from .models import Event, Profile, Message

# Register your models here.
admin.site.register(Event)
admin.site.register(Profile)
admin.site.register(Message)