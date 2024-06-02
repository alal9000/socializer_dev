from datetime import datetime, timedelta
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib.messages import get_messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from allauth.account.views import SignupView, LoginView
from django.db.models import Q, Count, F, Value
from django.db.models.functions import Coalesce

from friends.models import Friend
from .models import Profile
from .decorators import check_profile_id
from notifications.models import Notification
from photos.models import Photo
from .forms import (
    ProfileForm,
    UserUpdateForm,
    ProfileDescriptionForm,
    CustomSignupForm,
    CustomLoginForm,
)
from events.models import Event


# function based views
def home(request):
    current_datetime = datetime.now()
    unread_count = 0
    if request.user.is_authenticated:
        user = request.user.profile
        unread_count = Notification.objects.filter(user=user, read=False).count()

    # filter out events that are past their starting time and that are full / need understanding for this
    all_events = (
        Event.objects.annotate(
            num_guests=Count("guests"),
            num_attendees=Coalesce(
                F("num_guests") + Value(1), Value(0)
            ),  # add 1 for the host
        )
        .filter(
            Q(event_date__gt=current_datetime.date())
            | Q(
                event_date=current_datetime.date(),
                event_time__gte=current_datetime.time(),
            )
        )
        .filter(
            Q(total_attendees__isnull=True) | Q(num_attendees__lt=F("total_attendees"))
        )
        .order_by("-date_created")
    )

    print(all_events)

    # pagination logic
    events_per_page = 12
    paginator = Paginator(all_events, events_per_page)
    page_number = request.GET.get("page")

    try:
        events = paginator.page(page_number)
    except PageNotAnInteger:
        events = paginator.page(1)
    except EmptyPage:
        events = paginator.page(paginator.num_pages)

    storage = get_messages(request)
    success_message = None
    for message in storage:
        if message.tags == "success":
            success_message = message

    context = {
        "events": events,
        "success_message": success_message,
        "unread_count": unread_count,
    }

    return render(request, "app/dashboard.html", context)


def recommendations(request):
    return render(request, "app/recommendations.html")


def about(request):
    return render(request, "app/about.html")


def contact(request):
    return render(request, "app/contact.html")


def profile(request, profile_id):
    current_user_profile = request.user.profile
    profile = Profile.objects.get(id=profile_id)
    user_photos = Photo.objects.filter(profile=profile).order_by("-timestamp")[:6]
    user_instance = profile.user

    # Determine friendship status
    friend_status = None
    if Friend.objects.filter(sender=current_user_profile, receiver=profile).exists():
        friend_status = Friend.objects.get(
            sender=current_user_profile, receiver=profile
        ).status
    elif Friend.objects.filter(sender=profile, receiver=current_user_profile).exists():
        friend_status = Friend.objects.get(
            sender=profile, receiver=current_user_profile
        ).status

    if friend_status == "pending":
        button = "Pending"
    elif friend_status == "accepted":
        button = "Accepted"
    elif friend_status == "denied":
        button = "Add"
    else:
        button = "Add"

    current_datetime = timezone.now()
    twenty_four_hours_ago = current_datetime - timedelta(hours=24)
    twenty_four_hours_ago_date = twenty_four_hours_ago.date()
    twenty_four_hours_ago_time = twenty_four_hours_ago.time()

    # Filter attended events
    attended_events = Event.objects.filter(guests=profile).filter(
        event_date__gte=twenty_four_hours_ago_date
    ).filter(
        event_date=twenty_four_hours_ago_date,
        event_time__gte=twenty_four_hours_ago_time,
    ) | Event.objects.filter(
        guests=profile
    ).filter(
        event_date__gt=twenty_four_hours_ago_date
    )

    # Filter hosted events
    hosted_events = Event.objects.filter(host=profile).filter(
        event_date__gte=twenty_four_hours_ago_date
    ).filter(
        event_date=twenty_four_hours_ago_date,
        event_time__gte=twenty_four_hours_ago_time,
    ) | Event.objects.filter(
        host=profile
    ).filter(
        event_date__gt=twenty_four_hours_ago_date
    )

    # Get friends
    friends_as_sender = Friend.objects.filter(
        sender=profile, status="accepted"
    ).values_list("receiver", flat=True)
    friends_as_receiver = Friend.objects.filter(
        receiver=profile, status="accepted"
    ).values_list("sender", flat=True)
    friend_ids = list(friends_as_sender) + list(friends_as_receiver)
    friends = Profile.objects.filter(id__in=friend_ids)[:4]

    # initalize forms
    profile_form = ProfileForm(instance=profile)
    user_form = UserUpdateForm(instance=user_instance)
    description_form = ProfileDescriptionForm(instance=profile)

    # handle form submissions
    if request.method == "POST":
        print(request.POST)
        # profile pic form
        if "profile-pic" in request.POST:
            profile_form = ProfileForm(request.POST, request.FILES, instance=profile)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, "Profile picture updated successfully.")
                return redirect("profile", profile_id=profile_id)

        # friend / unfriend form
        if "friend-button" in request.POST:
            if request.POST["friend-button"] == "Add":
                button = "Pending"
                if not Friend.objects.filter(
                    sender=current_user_profile, receiver=profile, status="pending"
                ).exists():
                    Friend.objects.create(
                        sender=current_user_profile, receiver=profile, status="pending"
                    )
                    Notification.objects.create(
                        user=profile,
                        message="You have a new friend request",
                        link=reverse("friend_requests", args=[profile_id]),
                    )
            else:
                button = "Add"
                Friend.objects.get(
                    sender=request.user.profile,
                    receiver=Profile.objects.get(id=profile_id),
                ).delete()

        # description form
        if "update-description" in request.POST:
            description_form = ProfileDescriptionForm(request.POST, instance=profile)
            if description_form.is_valid():
                description_form.save()
                messages.success(request, "User description updated successfully.")
                return redirect("profile", profile_id=profile_id)

    storage = get_messages(request)
    success_message = None
    for message in storage:
        if message.tags == "success":
            success_message = message

    context = {
        "profile_form": profile_form,
        "user_form": user_form,
        "user_photos": user_photos,
        "attended_events": attended_events,
        "hosted_events": hosted_events,
        "profile": profile,
        "friends": friends,
        "button": button,
        "description_form": description_form,
        "success_message": success_message,
    }

    return render(request, "app/profile.html", context)


@login_required
@check_profile_id
def profile_settings(request, profile_id):
    profile = get_object_or_404(Profile, id=profile_id)
    user_instance = profile.user
    user_form = UserUpdateForm(instance=user_instance)

    if "user-details" in request.POST:
        user_form = UserUpdateForm(request.POST, instance=user_instance)
        if user_form.is_valid():
            user_form.save()
            messages.success(request, "User details updated successfully.")
            return redirect("profile_settings", profile_id=profile_id)

    context = {
        "profile": profile,
        "user_form": user_form,
    }

    return render(request, "app/settings.html", context)


@login_required
def delete_account(request):
    if request.method == "POST":
        profile = Profile.objects.get(user=request.user)
        profile.delete()
        request.user.delete()
        logout(request)
        messages.success(
            request,
            "Your account and associated profile have been successfully deleted.",
        )
        return redirect("home")


# class based views
class CustomSignupView(SignupView):
    form_class = CustomSignupForm
    template_name = "account/signup.html"
    default_success_url = reverse_lazy("home")

    def get_success_url(self):
        return self.default_success_url

    def form_valid(self, form):
        response = super().form_valid(form)
        first_name = form.cleaned_data.get("first_name")
        messages.success(
            self.request,
            f"Welcome, {first_name}! Your account was created successfully.",
        )

        return response


class CustomLoginView(LoginView):
    form_class = CustomLoginForm
    template_name = "account/login.html"

    def get_success_url(self):
        return reverse_lazy("home")

    def form_valid(self, form):
        response = super().form_valid(form)
        first_name = self.request.user.first_name
 
        messages.success(
            self.request, f"Welcome, {first_name}! You have successfully logged in."
        )
        
        return response
