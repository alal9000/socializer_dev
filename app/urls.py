from django.urls import path, include
from . import views
from .views import CustomSignupView, CustomLoginView

urlpatterns = [
  path('', views.home, name="home"),
  path('create', views.create, name="create"),
  path('about', views.about, name="about"),
  path('recommendations', views.recommendations, name="recommendations"),
  path('contact', views.contact, name="contact"),
  path('messages/<int:pk>', views.direct_messages, name='messages'),
  path('event/<int:pk>/', views.event, name="event"),
  path('event/<int:event_id>/remove_attendee/', views.remove_attendee, name='remove_attendee'),
  # all_auth urls
  path('accounts/login/', CustomLoginView.as_view(), name='account_login'),
  path('accounts/signup/', CustomSignupView.as_view(), name='account_signup'),
  path('accounts/profile/<int:profile_id>', views.profile, name='profile'),
  path('accounts/profile/<int:profile_id>/settings', views.profile_settings, name='profile_settings'),
  # notification urls
  path('notifications/', views.notifications, name='notifications'),
  path('mark-as-read/<int:notification_id>/', views.mark_notification_as_read, name='mark_as_read'),
  path('mark-all-as-read/', views.mark_all_notifications_as_read, name='mark_all_as_read'),
  # messages
  path('conversation/<int:sender_id>/<int:receiver_id>/', views.conversation_view, name='conversation'),
  # photo gallery
  path('photos/', include('photos.urls')),
]

