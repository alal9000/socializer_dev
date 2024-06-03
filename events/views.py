from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.contrib import messages
from django.http import HttpResponseRedirect

from . models import Event, Comment
from app.forms import EventForm
from notifications.models import Notification


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

    return render(request, "events/create.html", {
        "form": form
    })


def event(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    request_profile = None
    if request.user.is_authenticated:
        request_profile = request.user.profile

    is_guest = request_profile in event.guests.all()
    is_host = event.host == request_profile

    # calcuate how many currently registered attendees
    total_current_attendees = event.guests.count() + 1

    if request.method == 'POST':
        # comment
        if is_guest or is_host:
            comment_text = request.POST.get('comment_text')
            Comment.objects.create(profile=request_profile, event=event, comment=comment_text)

            # notify attendees when a comment is added
            attendees = [event.host] + list(event.guests.all())
            for attendee in attendees:
                if attendee != request_profile:
                    Notification.objects.create(
                            user=attendee,
                            message=f'{request_profile} commented in {event.event_title}',
                            link=reverse('event', kwargs={'pk': event.pk})
                        )

            return redirect('event', pk=event_id)

        # join event
        if request.user.is_authenticated and not is_host:
            event.guests.add(request_profile)

            Notification.objects.create(
                user=event.host,
                message=f'{request.user.first_name} just joined your event',
                link=reverse('event', kwargs={'pk': event.pk})
                )

            return redirect('event', pk=event_id)  

    
    comments = Comment.objects.filter(event=event)

    context = {
        'event': event,
        'is_guest': is_guest,
        'comments': comments,
        'is_host': is_host,
        'total_current_attendees': total_current_attendees,
    }

    return render(request, 'events/event.html', context)


@login_required
def remove_attendee(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    request_profile = request.user.profile

    if request_profile in event.guests.all():
        event.guests.remove(request_profile)
        messages.success(request, 'Successfully removed from the event.')
    else:
        messages.error(request, 'You are not currently attending this event.')

    return redirect('home')
