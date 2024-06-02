from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from app.models import Profile
from .models import Album, Photo
from app.decorators import check_profile_id

# Create your views here.
def gallery(request, profile_id):
    profile = get_object_or_404(Profile, id=profile_id)

    category = request.GET.get("category")
    if category == None:
        photos = Photo.objects.filter(profile=profile)
    else:
        photos = Photo.objects.filter(profile=profile, category__name=category)

    categories = Album.objects.all()

    context = {"categories": categories, "photos": photos, "profile": profile}

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
    categories = Album.objects.all()

    if request.method == "POST":
        data = request.POST
        images = request.FILES.getlist("images")

        if data["category"] != "none":
            category = Album.objects.get(id=data["category"])
        elif data["category_new"] != "":
            category, created = Album.objects.get_or_create(
                name=data["category_new"]
            )
        else:
            category = None

        for image in images:
            Photo.objects.create(
            category=category,
            description=data["description"],
            image=image,
            profile=profile,
        )

        return redirect("gallery", profile_id=profile_id)

    context = {"categories": categories, "profile": profile}

    return render(request, "photos/add_photos.html", context)



@login_required
@check_profile_id
def addAlbum(request, profile_id):
    profile = get_object_or_404(Profile, id=profile_id)

    if request.method == "POST":
        data = request.POST
        print("Here is the data dict: ", data)

        if data["album"] != "":
            Album.objects.create(name=data["album"])
            return redirect('gallery', profile_id=profile_id)

    context = {
        "profile": profile
    }


    return render(request, "photos/add_album.html", context)
