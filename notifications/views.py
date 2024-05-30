from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from . models import Notification

@login_required
def notifications(request):
    user_profile = request.user.profile
    notifications = user_profile.notification_set.filter(read=False).order_by('-timestamp')
    return render(request, 'notifications/notifications.html', {'notifications': notifications})


@login_required
def mark_notification_as_read(request, notification_id):
    notification = Notification.objects.get(id=notification_id)
    notification.read = True
    notification.save()
    return JsonResponse({'success': True})


@login_required
def mark_all_notifications_as_read(request):
    user_profile = request.user.profile
    user_profile.notification_set.filter(read=False).update(read=True)
    return JsonResponse({'success': True})
