from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from django.contrib.auth.models import User
from .models import Profile

from django.conf import settings


# Create Profile when User is created and saved, with the same name, email and a default about
def createProfile(sender, instance, created, **kwargs):
    if created:
        user = instance
        profile = Profile.objects.create(
            user=user,
            email=user.email,
            name=user.name,
            about="I am a Singapore Explorer" # default about, user can edit it
        )


# When Profile is updated, update the User
def updateUser(sender, instance, created, **kwargs):
    profile = instance
    user = profile.user

    if created == False:
        user.name = profile.name
        user.email = profile.email
        user.save()


# When profile is deleted, user is deleted also
def deleteUser(sender, instance, **kwargs):
    try:
        user = instance.user
        user.delete()
    except:
        pass

post_save.connect(createProfile, sender=User)
post_save.connect(updateUser, sender=Profile)
post_delete.connect(deleteUser, sender=Profile)
