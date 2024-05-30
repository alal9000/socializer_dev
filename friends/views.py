from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from . models import Friend

# Create your views here.
def friends(request, pk):
    friends = Friend.objects.all()
    return render(request, 'friends/friends.html', {"friends": friends})


def friend_requests(request):
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
        
        return redirect('friend_requests')

    # profile = get_object_or_404(Profile, id=profile_id)

    # print("profile is: ", profile)

    requests = Friend.objects.filter(status='pending', receiver=request.user.profile)

    print("queryset is: ", requests)

    context = {
        'requests': requests,
    }

    return render(request, 'friends/friend_requests.html', context)