from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Max
from django.utils import timezone

from .models import Message
from app.decorators import check_profile_id
from app.models import Profile
from notifications.models import Notification


@login_required
@check_profile_id
def direct_messages(request, profile_id):
    current_profile = get_object_or_404(Profile, id=profile_id)

    # Get distinct sender IDs
    sender_ids = Message.objects.filter(receiver=current_profile).values('sender').distinct()
    
    # Fetch the Profile objects for these sender IDs
    senders = Profile.objects.filter(id__in=[sender['sender'] for sender in sender_ids])

    context = {
        "senders": senders,
        "receiver": current_profile,
    }

    return render(request, "direct_messages/messages.html", context)


@login_required
def send_message(request, profile_id):
    # Messages sent from recipients profile

    receiver_profile = get_object_or_404(Profile, id=profile_id)
    sender_profile = request.user.profile
    message_text = request.POST.get("message")

    if message_text:
        Message.objects.create(
            sender=sender_profile,
            receiver=receiver_profile,
            message=message_text,
            timestamp=timezone.now(),
        )

        Notification.objects.create(
            user=receiver_profile,
            message=f"You have a new message from {sender_profile}",
            link=f"/direct_messages/conversation/{sender_profile.id}/{receiver_profile.id}",
        )
        messages.success(request, "Message sent successfully.")

        return redirect("home")

    else:
        messages.success(request, "Message did not send successfully.")
        return redirect("home")


def conversation_view(request, sender_id, receiver_id):
    # page requester is the same as current_profile
    if request.user.profile.pk == int(receiver_id):
        sender_profile = get_object_or_404(Profile, id=sender_id)
        receiver_profile = get_object_or_404(Profile, id=receiver_id)

        messages_sent_by_sender = Message.objects.filter(
            sender=sender_profile, receiver=receiver_profile
        )
        messages_sent_by_receiver = Message.objects.filter(
            sender=receiver_profile, receiver=sender_profile
        )
        conversation_messages = (
            # combine qsets with django union operator and order by latest message
            messages_sent_by_sender | messages_sent_by_receiver
        ).order_by("timestamp")


        if request.method == "POST":
            message_text = request.POST.get("message")

            if message_text:
                Message.objects.create(
                    sender=receiver_profile,
                    receiver=sender_profile,
                    message=message_text,
                    timestamp=timezone.now(),
                )

                Notification.objects.create(
                    user=sender_profile,
                    message=f"You have a new message from {receiver_profile}",
                    link=f"/direct_messages/conversation/{receiver_profile.id}/{sender_profile.id}",
                )

            return redirect(
                "conversation",
                sender_id=sender_profile.id,
                receiver_id=receiver_profile.id,
            )

        return render(
            request,
            "direct_messages/conversation.html",
            {
                "messages": conversation_messages,
                "sender": sender_profile,
                "receiver": receiver_profile,
            },
        )
    else:
        return redirect("home")
