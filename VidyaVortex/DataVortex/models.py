# models.py for VidyaVortex project 2015-2016

from django.db import models
from django.contrib.auth.models import User, Group
from django.core.validators import MinValueValidator, URLValidator
from django.core.exceptions import ValidationError
from decimal import Decimal


# general (global) game object model
class Game(models.Model):

    # checks if image file size is not over 5MB and it has valid file extension
    def image_check(fieldfile_obj):
        extension = fieldfile_obj.file.name.split('.')[1]
        filesize = fieldfile_obj.file.size
        megabyte_limit = 5.0
        if filesize > megabyte_limit*1024*1024:
            raise ValidationError("Max image size is %sMB" % str(megabyte_limit))
        if extension != "png" and extension != "jpg" and extension != "gif":
            raise ValidationError("Supported file formats are: png, jpg, gif")

    id = models.PositiveIntegerField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)
    buycount = models.PositiveIntegerField(default=0)
    url = models.URLField(max_length=200, unique=True, default="https://example.com/game.html",
                          validators=[URLValidator(schemes=["https"], message="Please provide a valid https URL")])
    description = models.TextField(blank=True)
    # thumbnail = models.FileField(upload_to='thumbnails', null=True, validators=[image_check]) 
    # had to discard file uploading feature as Heroku is unwilling to host anything in MEDIA_ROOT for some reason
    thumbnail = models.URLField(max_length=200, blank=True, null=True, default="https://example.com/myimage.png")
    price = models.DecimalField(max_digits=7, decimal_places=2, default=0,
                                validators=[MinValueValidator(Decimal('0.00'))])
    rating = models.IntegerField(default=0)
    time = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        ordering = ['name']


# user spesific game object model
class MyGame(models.Model):
    game = models.ForeignKey(Game, blank=True, null=True)
    player = models.ForeignKey(User, blank=True, null=True)
    gamestate = models.TextField(blank=True)
    rated = models.BooleanField(default=False)

    class Meta:
        ordering = ['game']


# highscore object model with relations to both above objects
class Highscore(models.Model):
    value = models.FloatField()
    game = models.ForeignKey(Game, blank=True, null=True)
    mygame = models.ForeignKey(MyGame, blank=True, null=True)
    
    class Meta:
        ordering = ['-value']


# used to track information on purchases of games
class Purchase(models.Model):
    amount = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    buyer = models.ForeignKey(User, blank=True, null=True)
    game = models.ForeignKey(Game, blank=True, null=True)
    time = models.DateTimeField(auto_now_add=True)
    valid = models.BooleanField(default=False)


# used to check if user has completed email verification
# apikey is also included in verification email which enables the use of this web service's non public api 
class Verification(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    verified = models.BooleanField(default=False)
    apikey = models.CharField(max_length=32, unique=True)
