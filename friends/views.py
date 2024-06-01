from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from app.decorators import check_profile_id
from django.contrib.auth.decorators import login_required
from . models import Friend
from app.models import Profile

# Create your views here.
def friends(request):
    friends = Friend.objects.all()
    return render(request, 'friends/friends.html', {"friends": friends})

@login_required
@check_profile_id
def friend_requests(request, profile_id ):
    profile = get_object_or_404(Profile, id=profile_id)
    if request.method == "POST":
        friend_request_id = request.POST.get('friend_request_id')
        action = request.POST.get('action')

        if friend_request_id and action:
            friend_request = get_object_or_404(Friend, id=friend_request_id, receiver=request.user.profile)

            if action == "approve":
                friend_request.status = 'accepted'
                friend_request.save()
                messages.success(request, "Friend request approved.")
            elif action == "deny":
                friend_request.status = 'denied'
                friend_request.save()
                messages.success(request, "Friend request denied.")
        
        return redirect('profile', profile_id)

    # profile = get_object_or_404(Profile, id=profile_id)

    # print("profile is: ", profile)

    requests = Friend.objects.filter(status='pending', receiver=request.user.profile)

    print("queryset is: ", requests)

    context = {
        'requests': requests,
    }

    return render(request, 'friends/friend_requests.html', context)