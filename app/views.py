from datetime import timedelta
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.db.models import Max, Count, F, Q
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.messages import get_messages
from django.http import HttpResponseRedirect, JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from allauth.account.views import SignupView, LoginView

from app.models import Event, Comment, Profile, Follow, Message, Notification
from photos.models import Photo
from . forms import ProfileForm, EventForm, UserUpdateForm, ProfileDescriptionForm


# function based views
def home(request):
    current_datetime = timezone.now()
    twenty_four_hours_ago = current_datetime - timedelta(hours=24)
    unread_count = 0
    if request.user.is_authenticated:
        user = request.user.profile
        unread_count = Notification.objects.filter(user=user, read=False).count()
    
    # filter out events that are full and over 24 hours old
    all_events = Event.objects.filter(
        event_date__gte=twenty_four_hours_ago.date(),
        event_time__gte=twenty_four_hours_ago.time(),
    ).order_by('-date_created')

    print(all_events)

    # pagination logic
    events_per_page = 12
    paginator = Paginator(all_events, events_per_page)
    page_number = request.GET.get('page')

    try:
        events = paginator.page(page_number)
    except PageNotAnInteger:
        events = paginator.page(1)
    except EmptyPage:
        events = paginator.page(paginator.num_pages)

    storage = get_messages(request)
    success_message = None
    for message in storage:
        if message.tags == 'success':
            success_message = message

    context = {
        'events': events, 
        'success_message': success_message, 
        'unread_count': unread_count
    }

    return render(request, 'app/dashboard.html', context)

@login_required(login_url='account_login')
def create(request):
    current_user_profile = request.user.profile
    form = EventForm()

    # create event form
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            new_event = form.save(commit=False)
            if current_user_profile:
                new_event.host = current_user_profile          
                new_event.save()
                messages.success(request, 'Event created successfully.')
                
                return HttpResponseRedirect(reverse('home'))
            else:
                messages.error(request, 'Error creating event. User profile not found.')

    return render(request, "app/create.html", {
        "form": form
    })



def recommendations(request):
    return render(request, 'app/recommendations.html')



def about(request):
    return render(request, 'app/about.html')



def contact(request):
    return render(request, 'app/contact.html')


@login_required(login_url='account_login')
def event(request, pk):
    event = Event.objects.get(id=pk)
    current_profile = request.user.profile
    is_guest = current_profile in event.guests.all()
    is_host = event.host == current_profile

    # calcuate how many currently registered attendees
    total_current_attendees = event.guests.count() + 1

    if request.method == 'POST':
        # comment
        if is_guest or is_host:
            comment_text = request.POST.get('comment_text')
            Comment.objects.create(profile=current_profile, event=event, comment=comment_text)

            # notify attendees when a comment is added
            attendees = [event.host] + list(event.guests.all())
            for attendee in attendees:
                if attendee != current_profile:
                    Notification.objects.create(
                            user=attendee,
                            message=f'{current_profile} commented in {event.event_title}',
                            link=reverse('event', kwargs={'pk': event.pk})
                        )

            return redirect('event', pk=pk)

        # join event
        if request.user.is_authenticated and not is_host:
            event.guests.add(current_profile)

            Notification.objects.create(
                user=event.host,
                message=f'{request.user.first_name} just joined your event',
                link=reverse('event', kwargs={'pk': event.pk})
                )

            return redirect('event', pk=pk)  

    
    comments = Comment.objects.filter(event=event)

    context = {
        'event': event,
        'is_guest': is_guest,
        'comments': comments,
        'is_host': is_host,
        'total_current_attendees': total_current_attendees,
    }

    return render(request, 'app/event.html', context)


def profile(request, profile_id):
    profile = Profile.objects.get(id=profile_id)
    user_photos = Photo.objects.filter(profile=profile).order_by('-timestamp')[:6]
    user_instance = profile.user
    button = "Follow" if not Follow.objects.filter(follower=request.user.profile, following=profile_id) else "Unfollow"
    current_datetime = timezone.now()
    twenty_four_hours_ago = current_datetime - timedelta(hours=24)
    twenty_four_hours_ago_date = twenty_four_hours_ago.date()
    twenty_four_hours_ago_time = twenty_four_hours_ago.time()

    # Filter attended events
    attended_events = Event.objects.filter(
        guests=profile
    ).filter(
        event_date__gte=twenty_four_hours_ago_date
    ).filter(
        event_date=twenty_four_hours_ago_date,
        event_time__gte=twenty_four_hours_ago_time
    ) | Event.objects.filter(
        guests=profile
    ).filter(
        event_date__gt=twenty_four_hours_ago_date
    )

    # Filter hosted events
    hosted_events = Event.objects.filter(
        host=profile
    ).filter(
        event_date__gte=twenty_four_hours_ago_date
    ).filter(
        event_date=twenty_four_hours_ago_date,
        event_time__gte=twenty_four_hours_ago_time
    ) | Event.objects.filter(
        host=profile
    ).filter(
        event_date__gt=twenty_four_hours_ago_date
    )

    followers = Follow.objects.filter(following=profile_id)[:6]
    following = Follow.objects.filter(follower=profile_id)[:6]

    #initalize forms
    profile_form = ProfileForm(instance=profile)
    user_form = UserUpdateForm(instance=user_instance)
    description_form = ProfileDescriptionForm(instance=profile)

    # handle form submissions
    if request.method == 'POST':
        print(request.POST)
        # profile pic form
        if "profile-pic" in request.POST:
            profile_form = ProfileForm(request.POST, request.FILES, instance=profile)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, 'Profile picture updated successfully.')
                return redirect('profile', profile_id=profile_id)

        if "user-details" in request.POST:
            user_form = UserUpdateForm(request.POST, instance=user_instance)
            if user_form.is_valid():
                user_form.save()
                messages.success(request, 'User details updated successfully.')
                return redirect('profile', profile_id=profile_id)

        # follow / unfollow form
        if "follow-button" in request.POST:
            if request.POST["follow-button"] == "Follow":
                button = "Unfollow"
                Follow.objects.create(follower=request.user.profile, following=Profile.objects.get(id=profile_id))
            else:
                button = 'Follow'
                Follow.objects.get(follower=request.user.profile, following=Profile.objects.get(id=profile_id)).delete()
        
        # description form
        if "update-description" in request.POST:
                description_form = ProfileDescriptionForm(request.POST, instance=profile)
                if description_form.is_valid():
                    description_form.save()
                    messages.success(request, 'User description updated successfully.')
                    return redirect('profile', profile_id=profile_id)


    storage = get_messages(request)
    success_message = None
    for message in storage:
        if message.tags == 'success':
            success_message = message
        

    context = {
        "profile_form": profile_form,
        "user_form": user_form,
        "user_photos": user_photos,
        "attended_events": attended_events, 
        "hosted_events": hosted_events, 
        "profile":profile,
        "followers": followers,
        "following": following,
        "button": button,
        "description_form": description_form,
        "success_message": success_message
    }

    return render(request, "app/profile.html", context)


@login_required
def profile_settings(request, profile_id):
    profile = get_object_or_404(Profile, id=profile_id)
    user_instance =profile.user
    user_form = UserUpdateForm(instance=user_instance)

    context = {
        'profile': profile,
        "user_form": user_form,
    }

    return render(request, "app/settings.html", context)

@login_required
def remove_attendee(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    current_user_profile = request.user.profile

    if current_user_profile in event.guests.all():
        event.guests.remove(current_user_profile)
        messages.success(request, 'Successfully removed from the event.')
    else:
        messages.error(request, 'You are not currently attending this event.')

    return redirect('home')


# messages views

@login_required
def direct_messages(request, pk):
    if request.user.profile.pk != int(pk):
        messages.error(request, "You do not have permission to view this page.")
        return redirect('home')

    receiver_profile = Profile.objects.get(id=pk)
    
    latest_message_ids = (
        Message.objects
        .filter(receiver=receiver_profile)
        .values('sender')
        .annotate(latest_message_id=Max('id'))
        .values_list('latest_message_id', flat=True)
    )
    latest_messages = Message.objects.filter(id__in=latest_message_ids)

    senders = Profile.objects.filter(id__in=latest_messages.values_list('sender', flat=True))

    # DM from profile page
    if request.method == 'POST':
        message_text = request.POST.get('message')
        sender_profile = request.user.profile
        recipient_profile = Profile.objects.get(id=pk)

        if message_text:
                Message.objects.create(
                    sender=sender_profile,
                    receiver=recipient_profile,
                    message=message_text,
                    timestamp=timezone.now()
                )

                Notification.objects.create(
                user=receiver_profile,
                message='You have a new message',
                link=f'/messages/{receiver_profile.id}'
                )

        return redirect('profile', pk=pk)

    context = {
        "senders": senders,
        "receiver": receiver_profile,
        "latest_messages": latest_messages
    }

    return render(request, "app/messages.html", context)


@login_required
def conversation_view(request, sender_id, receiver_id):
    if request.user.profile.pk == int(receiver_id):
        sender_profile = get_object_or_404(Profile, id=sender_id)
        receiver_profile = get_object_or_404(Profile, id=receiver_id)

        messages_sent_by_sender = Message.objects.filter(sender=sender_profile, receiver=receiver_profile)
        messages_sent_by_receiver = Message.objects.filter(sender=receiver_profile, receiver=sender_profile)
        conversation_messages = messages_sent_by_sender | messages_sent_by_receiver
        conversation_messages = conversation_messages.order_by('timestamp')

        unread_messages = conversation_messages.filter(is_read=False)
        unread_messages.update(is_read=True)

        if request.method == 'POST':
            message_text = request.POST.get('message')

            if message_text:
                    Message.objects.create(
                        sender=receiver_profile,
                        receiver=sender_profile,
                        message=message_text,
                        timestamp=timezone.now()
                    )

                    Notification.objects.create(
                    user=receiver_profile,
                    message='You have a new message',
                    link='/messages/'
                    )

            return redirect('conversation', sender_id=sender_profile.id, receiver_id=receiver_profile.id)


        return render(request, "app/conversation.html", {"messages": conversation_messages, "sender": sender_profile, "receiver": receiver_profile})
    else:
        messages.error(request, "You do not have permission to view this page.")
        return redirect('home')



# notification views
@login_required
def notifications(request):
    user_profile = request.user.profile
    notifications = user_profile.notification_set.filter(read=False).order_by('-timestamp')
    return render(request, 'app/notifications.html', {'notifications': notifications})


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


def following(request, pk):
    following = Follow.objects.filter(follower=pk)
    return render(request, 'app/following.html', {"following": following})



def followers(request, pk):
    followers = Follow.objects.filter(following=pk)
    return render(request, 'app/followers.html', {"followers": followers})


# class based views
class CustomSignupView(SignupView):
    default_success_url = reverse_lazy('home')

    def get_success_url(self):
        return self.default_success_url

    def form_valid(self, form):
        response = super().form_valid(form)
        first_name = form.cleaned_data.get('first_name') 
        if first_name:
            messages.success(self.request, f"Welcome, {first_name}! Your account was created successfully.")
        else:
            messages.success(self.request, "Welcome! Your account was created successfully.")
        return response


class CustomLoginView(LoginView):
    def get_success_url(self):
        return reverse_lazy('home')

    def form_valid(self, form):
        response = super().form_valid(form)
        first_name = self.request.user.first_name
        if first_name:
            messages.success(self.request, f"Welcome, {first_name}! You have successfully logged in.")
        else:
            messages.success(self.request, "Welcome! You have successfully logged in.")
        return response


