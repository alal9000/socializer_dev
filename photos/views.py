from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required

from app.models import Profile
from .models import Album, Photo
from app.decorators import check_profile_id


def gallery(request, profile_id):
    profile = get_object_or_404(Profile, id=profile_id)

    album = request.GET.get("album")
    if album == None:
        photos = Photo.objects.filter(profile=profile)
    else:
        photos = Photo.objects.filter(profile=profile, album__name=album)

    albums = Album.objects.filter(profile=profile)

    # Pagination
    page = request.GET.get('page', 1)
    paginator = Paginator(photos, 10)

    try:
        photos = paginator.page(page)
    except PageNotAnInteger:
        photos = paginator.page(1)
    except EmptyPage:
        photos = paginator.page(paginator.num_pages)
    # end

    if request.method == 'POST':
        data = request.POST
        if "album_id" in data:
            # get POST data dict
            # extract data from form submission
            album_id = data['album_id']
            # retrieve associated album object associated with the form submission and remove it
            album = Album.objects.get(id=album_id)
            album.delete()

            messages.success(request, "Album removed successfully")
            return redirect('gallery', profile_id=profile_id)

        else:
            photo_id = data['photo_id']
            photo = Photo.objects.get(id=photo_id)
            photo.delete()

            messages.success(request, "Photo removed successfully")
            return redirect('gallery', profile_id=profile_id)

    context = {
        "albums": albums, 
        "photos": photos, 
        "profile": profile
    }

    return render(request, "photos/gallery.html", context)


def viewPhoto(request, profile_id, photo_id):
    profile = get_object_or_404(Profile, id=profile_id)
    photo = get_object_or_404(Photo, id=photo_id, profile=profile)

    context = {"photo": photo, "profile": profile}

    return render(request, "photos/photo.html", context)


@login_required
@check_profile_id
def addPhoto(request, profile_id):
    profile = get_object_or_404(Profile, id=profile_id)
    albums = Album.objects.filter(profile=profile)

    if request.method == "POST":
        data = request.POST
        images = request.FILES.getlist("images")

        if data["album"] != "none":
            album = Album.objects.get(id=data["album"])
        elif data["album_new"] != "":
            album, created = Album.objects.get_or_create(
                name=data["album_new"], profile=profile
            )
        else:
            album = None

        for image in images:
            Photo.objects.create(
            album=album,
            description=data["description"],
            image=image,
            profile=profile,
        )

        return redirect("gallery", profile_id=profile_id)

    context = {"albums": albums, "profile": profile}

    return render(request, "photos/add_photos.html", context)



@login_required
@check_profile_id
def addAlbum(request, profile_id):
    profile = get_object_or_404(Profile, id=profile_id)

    if request.method == "POST":
        data = request.POST
        print("Here is the data dict: ", data)

        if data["album"] != "":
            Album.objects.create(name=data["album"], profile=profile)

            messages.success(request, "Album added successfully")
            return redirect('gallery', profile_id=profile_id)

    context = {
        "profile": profile
    }

    return render(request, "photos/add_album.html", context)
