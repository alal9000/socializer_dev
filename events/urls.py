from django.urls import path
from . import views

urlpatterns = [
  path('event/<int:event_id>/', views.event, name="event"),
  path('event/<int:event_id>/remove_attendee/', views.remove_attendee, name='remove_attendee'),
  path('create', views.create, name="create"),
]

