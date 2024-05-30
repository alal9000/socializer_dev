from datetime import timedelta
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.db.models import Max, Count, F, Q
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.messages import get_messages
from django.http import HttpResponseRedirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from allauth.account.views import SignupView, LoginView
from friends.models import Friend

from app.models import Event, Comment, Profile
from notifications.models import Notification
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
    current_user_profile = request.user.profile
    profile = Profile.objects.get(id=profile_id)
    print(profile.id)
    user_photos = Photo.objects.filter(profile=profile).order_by('-timestamp')[:6]
    user_instance = profile.user
    
    # Determine friendship status
    friend_status = None
    if Friend.objects.filter(sender=current_user_profile, receiver=profile).exists():
        friend_status = Friend.objects.get(sender=current_user_profile, receiver=profile).status
    elif Friend.objects.filter(sender=profile, receiver=current_user_profile).exists():
        friend_status = Friend.objects.get(sender=profile, receiver=current_user_profile).status

    if friend_status == 'pending':
        button = 'Pending'
    elif friend_status == 'accepted':
        button = 'Accepted'
    elif friend_status == 'denied':
        button = 'Add'
    else:
        button = 'Add'



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

    # Get friends
    friends_as_sender = Friend.objects.filter(sender=profile, status='accepted').values_list('receiver', flat=True)
    friends_as_receiver = Friend.objects.filter(receiver=profile, status='accepted').values_list('sender', flat=True)
    friend_ids = list(friends_as_sender) + list(friends_as_receiver)
    friends = Profile.objects.filter(id__in=friend_ids)

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

        # friend / unfriend form
        if "friend-button" in request.POST:
            if request.POST["friend-button"] == "Add":
                button = "Pending"

                if not Friend.objects.filter(sender=current_user_profile, receiver=profile, status='pending').exists():
                    Friend.objects.create(sender=current_user_profile, receiver=profile, status='pending')
                    Notification.objects.create(user=profile, message="You have a new friend request", link=reverse('friend_requests'))

            else:
                button = 'Add'
                Friend.objects.get(sender=request.user.profile, receiver=Profile.objects.get(id=profile_id)).delete()
        
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
        "friends": friends,
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


