from app.models import Profile
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from . models import Category, Photo

# Create your views here.
def gallery(request, profile_id):
  profile = get_object_or_404(Profile, id=profile_id)

  category = request.GET.get('category')
  if category == None:
    photos = Photo.objects.filter(profile=profile)
  else:
    photos = Photo.objects.filter(profile=profile, category__name=category)


  categories = Category.objects.all()

  context = {
    'categories': categories,
    'photos': photos,
    'profile': profile
  }

  return render(request, 'photos/gallery.html', context)


def viewPhoto(request, profile_id, photo_id):
  profile = get_object_or_404(Profile, id=profile_id)
  photo = Photo.objects.get(id=photo_id, profile=profile)

  context = {
    'photo': photo,
    'profile': profile
  }

  return render(request, 'photos/photo.html', context)


def addPhoto(request, profile_id):
  if not request.user.is_authenticated:
      messages.error(request, "You need to be logged in to add a photo.")
      return redirect('login')

  profile = get_object_or_404(Profile, id=profile_id)

  if request.user.profile.id != profile_id:
      messages.error(request, "You are not authorized to add photos to this profile.")
      return redirect('home')
  
  categories = Category.objects.all()

  if request.method == 'POST':
      data = request.POST
      image = request.FILES.get('image')

      if data['category'] != 'none':
        category = Category.objects.get(id=data['category'])
      elif data['category_new'] != '':
        category, created = Category.objects.get_or_create(name=data['category_new'])
      else:
        category = None

      Photo.objects.create(
        category=category,
        description=data['description'],
        image=image,
        profile=profile
      )

      return redirect('gallery', profile_id=profile_id)

  context = {
    'categories': categories,
    'profile': profile
  }
  
  return render(request, 'photos/add.html', context)