from fileinput import FileInput
from django.forms import ModelForm, TextInput, Textarea, FileInput, TextInput, EmailInput, IntegerField,NumberInput
from django.contrib.auth.models import User
from django import forms
from allauth.account.forms import SignupForm, LoginForm

from . models import Profile, User
from events.models import Event

#create event
class EventForm(ModelForm):
  class Meta:
    model = Event
    fields = '__all__'
    exclude = ['user']
    widgets = {
            'description': Textarea(attrs={'rows': 4, 'maxlength': 500, 'class': 'form-control', 'placeholder': 'Write a description for your event...'}),
            'event_title': TextInput(attrs={'class': 'form-control', 'placeholder': 'Name for your event...'}),
            'total_attendees': NumberInput(attrs={'class': 'form-control', 'placeholder': 'Number of attendees inc host...'}),
        }


# profile pic upload
class ProfileForm(ModelForm):
  class Meta:
    model = Profile
    fields = ('profile_pic',)
    widgets = {
            'profile_pic': FileInput(attrs={'class': 'form-control'})
        }
    

# update user info
class UserUpdateForm(ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': TextInput(attrs={'class': 'form-control'}),
            'last_name': TextInput(attrs={'class': 'form-control'}),
            'email': EmailInput(attrs={'class': 'form-control'})
        }


# profile description form
class ProfileDescriptionForm(ModelForm):
    class Meta:
        model = Profile
        fields = ['description']
        widgets = {
            'description': forms.Textarea(attrs={
                'placeholder': 'Enter your profile description here...',
                'rows': 5,
                'cols': 40,
                'class': 'form-control',
            }),
        }


# user signup
class CustomSignupForm(SignupForm):

    first_name = forms.CharField(max_length=50, label='First Name')
    last_name = forms.CharField(max_length=50, label='Last Name')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.pop('username', None)
        self.fields['first_name'].widget.attrs.update({'class': 'form-control mb-2'})
        self.fields['last_name'].widget.attrs.update({'class': 'form-control mb-2'})
        self.fields['email'].widget.attrs.update({'class': 'form-control mb-2'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control mb-2'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control mb-2'})

    def signup(self, request, user):
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.save()

        return user


class CustomLoginForm(LoginForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.pop('username', None) 
        self.fields['login'].widget.attrs.update({'class': 'form-control mb-2'})
        self.fields['password'].widget.attrs.update({'class': 'form-control'})  

    def login(self, *args, **kwargs):

        return super().login(*args, **kwargs)
    