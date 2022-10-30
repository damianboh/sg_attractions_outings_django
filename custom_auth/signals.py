from django.db.models.signals import post_save, post_delete
from .models import User
from .models import Profile
from django.core.mail import send_mail
from django.conf import settings


# Create Profile when User is created and saved, with the same name, email and a default about
# Sends email to User when User is created
def createProfile(sender, instance, created, **kwargs):
    print("fired")
    if created:
        user = instance
        profile = Profile.objects.create(
            user=user,
            email=user.email,
            name=user.name,
            about="I am a Singapore Explorer" # default about, user can edit it
        )

        subject = 'Welcome to Singapore Attractions'
        message = 'We are to have you onboard! Feel free to search attractions and organise outings with your friends! Cheers!'

        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [profile.email],
            fail_silently=False,
        )
        


# When Profile is updated, update the User
def updateUser(sender, instance, created, **kwargs):
    print("fired")
    profile = instance
    user = profile.user

    # Only when Profile is updated, not created
    # or else signal will go into infinite loops when User created
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
