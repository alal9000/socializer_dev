from django.contrib import admin
from . models import Event, EventRequest

# Register your models here.
admin.site.register(Event)
admin.site.register(EventRequest)
