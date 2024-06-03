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

    receiver_profile = Profile.objects.get(id=profile_id)

    latest_message_ids = (
        Message.objects.filter(receiver=receiver_profile)
        .values("sender")
        .annotate(latest_message_id=Max("id"))
        .values_list("latest_message_id", flat=True)
    )
    latest_messages = Message.objects.filter(id__in=latest_message_ids)

    senders = Profile.objects.filter(
        id__in=latest_messages.values_list("sender", flat=True)
    )

    if request.method == 'POST':
        data = request.POST
        print("The data is: ", data)
        message_id = data['message_id']

        message = Message.objects.get(id=message_id)
        message.delete()
        messages.success(request, "Message deleted successfully.")

        return redirect('messages', profile_id=profile_id)


    context = {
        "senders": senders,
        "receiver": receiver_profile,
        "latest_messages": latest_messages,
    }

    return render(request, "direct_messages/messages.html", context)


@login_required
def send_message(request, pk):
    receiver_profile = Profile.objects.get(id=pk)
    message_text = request.POST.get("message")
    sender_profile = request.user.profile
    recipient_profile = Profile.objects.get(id=pk)

    if message_text:
        Message.objects.create(
            sender=sender_profile,
            receiver=recipient_profile,
            message=message_text,
            timestamp=timezone.now(),
        )

        Notification.objects.create(
            user=receiver_profile,
            message="You have a new message",
            link=f"/direct_messages/messages/{receiver_profile.id}",
        )
        messages.success(request, "Message sent successfully.")

        return redirect("home")
    
    else:
        messages.success(request, "Message did not send successfully.")
        return redirect("home")



def conversation_view(request, sender_id, receiver_id):
    if request.user.profile.pk == int(receiver_id):
        sender_profile = get_object_or_404(Profile, id=sender_id)
        receiver_profile = get_object_or_404(Profile, id=receiver_id)

        messages_sent_by_sender = Message.objects.filter(
            sender=sender_profile, receiver=receiver_profile
        )
        messages_sent_by_receiver = Message.objects.filter(
            sender=receiver_profile, receiver=sender_profile
        )
        conversation_messages = messages_sent_by_sender | messages_sent_by_receiver
        conversation_messages = conversation_messages.order_by("timestamp")

        # Filter unread messages based on the receiver
        unread_messages = conversation_messages.filter(is_read=False, receiver=receiver_profile)
        unread_messages.update(is_read=True)  

        if request.method == "POST":
            message_text = request.POST.get("message")
            print(message_text)

            if message_text:
                Message.objects.create(
                    sender=receiver_profile,
                    receiver=sender_profile,
                    message=message_text,
                    timestamp=timezone.now(),
                )

                Notification.objects.create(
                    user=sender_profile,
                    message="You have a new message",
                    link=f"/direct_messages/messages/{sender_profile.id}",
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
        messages.error(request, "You do not have permission to view this page.")
        return redirect("home")
