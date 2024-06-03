from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q

from app.decorators import check_profile_id
from django.contrib.auth.decorators import login_required
from .models import Friend
from app.models import Profile


@login_required
def friends(request, profile_id):
    profile = get_object_or_404(Profile, id=profile_id)

    friends = Friend.objects.filter(
        Q(sender=profile, status="accepted") | Q(receiver=profile, status="accepted")
    )

    other_friends = [friend.get_other_profile(profile) for friend in friends]

    return render(request, "friends/friends.html", {"friends": other_friends, "profile": profile})


@login_required
@check_profile_id
def friend_requests(request, profile_id):
    request_profile = request.user.profile
    if request.method == "POST":
        friend_request_id = request.POST.get("friend_request_id")
        action = request.POST.get("action")

        if friend_request_id and action:
            friend_request = get_object_or_404(
                Friend, id=friend_request_id, receiver=request_profile
            )

            if action == "approve":
                friend_request.status = "accepted"
                friend_request.save()
                messages.success(request, "Friend request approved.")
            elif action == "deny":
                friend_request.status = "denied"
                friend_request.save()
                messages.success(request, "Friend request denied.")

        return redirect("profile", profile_id)

    requests = Friend.objects.filter(status="pending", receiver=request_profile)

    context = {
        "requests": requests,
    }

    return render(request, "friends/friend_requests.html", context)
