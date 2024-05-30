from django.urls import path
from . import views

urlpatterns = [
  path('<int:pk>/', views.friends, name="friends"),
  path('requests/', views.friend_requests, name="friend_requests"),
]