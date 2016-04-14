# forms.py for VidyaVortex project 2015-2016

from django import forms
from DataVortex.models import Game


# Used for user registration, quite self-explanatory
class RegisterForm(forms.Form):
    username = forms.CharField(max_length=50, label="Username", required=True)
    email = forms.EmailField(label="Email address", required=True)
    password = forms.CharField(widget=forms.PasswordInput, label="Password", required=True)
    password2 = forms.CharField(widget=forms.PasswordInput, label="Repeat password", required=True)
    developer = forms.ChoiceField(required=True, widget=forms.RadioSelect,
                                  choices=(("dev", "Developer"), ("player", "Player"),), label="Select account type:")


# Simple verification form used to check if user really wants to delete his game
class BoolForm(forms.Form):
    accept = forms.BooleanField(label="accept", widget=forms.HiddenInput)


# used in addgame view, links certain Game model fields to this form
class UploadForm(forms.ModelForm):

    class Meta:
        model = Game
        fields = ('name', 'url', 'description', 'price', 'thumbnail')


# bound form with hidden inputs, used to communicate with payment service
class PurchaseForm(forms.Form):
    pid = forms.IntegerField(required=True, label="pid", widget=forms.HiddenInput)
    sid = forms.CharField(label="sid", widget=forms.HiddenInput)
    amount = forms.DecimalField(max_digits=9, decimal_places=2, label="amount", widget=forms.HiddenInput)
    success_url = forms.URLField(label="success_url", widget=forms.HiddenInput)
    cancel_url = forms.URLField(label="cancel_url", widget=forms.HiddenInput)
    error_url = forms.URLField(label="error_url", widget=forms.HiddenInput)
    checksum = forms.CharField(label="checksum", widget=forms.HiddenInput)


# extended UploadForm for editgame view. 
# The use of this form allows giving your game the same name and url as before when editing a game
class EditForm(forms.ModelForm):

    name = forms.CharField(max_length=100, label="name", required=False)
    url = forms.URLField(max_length=200, label="url", required=False)
    
    class Meta:
        model = Game
        fields = ('description', 'price', 'thumbnail')