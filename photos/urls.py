from django.urls import path
from . import views

urlpatterns = [
  path('<int:profile_id>/photo/<int:photo_id>/', views.viewPhoto, name='photo'),
  path('<int:profile_id>/', views.gallery, name='gallery'),
  path('<int:profile_id>/add/', views.addPhoto, name='add'),
]