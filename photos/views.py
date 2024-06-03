from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from app.models import Profile
from .models import Album, Photo
from app.decorators import check_profile_id

# Create your views here.
def gallery(request, profile_id):
    profile = get_object_or_404(Profile, id=profile_id)

    album = request.GET.get("album")
    if album == None:
        photos = Photo.objects.filter(profile=profile)
    else:
        photos = Photo.objects.filter(profile=profile, album__name=album)

    albums = Album.objects.filter(profile=profile)

    context = {"albums": albums, "photos": photos, "profile": profile}

    return render(request, "photos/gallery.html", context)


def viewPhoto(request, profile_id, photo_id):
    profile = get_object_or_404(Profile, id=profile_id)
    photo = Photo.objects.get(id=photo_id, profile=profile)

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
            return redirect('gallery', profile_id=profile_id)

    context = {
        "profile": profile
    }

    return render(request, "photos/add_album.html", context)
