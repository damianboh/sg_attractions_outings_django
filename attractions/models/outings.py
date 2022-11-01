from datetime import timedelta
from django.contrib.auth import get_user_model
from django.db import models
from .attractions import Attraction
from custom_auth.models import Profile
import uuid

UserModel = get_user_model() # from custom user model

# A creator creates outing for a particular attracton at a particular time
class Outing(models.Model):
    class Meta:
        ordering = ["-start_time"]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    attraction = models.ForeignKey(Attraction, on_delete=models.PROTECT)
    start_time = models.DateTimeField()
    creator = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="created_outings")
    start_notification_sent = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.attraction.name} by {self.creator.name} ({self.creator.email})"


class OutingInvitation(models.Model):
    class Meta:
        unique_together = [("invitee", "outing")]

    outing = models.ForeignKey(Outing, on_delete=models.CASCADE, related_name="outing_invites")
    invitee = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="invites")
    attendance_confirmed = models.BooleanField(default=False)
    is_attending = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.outing} / {self.invitee.name} ({self.invitee.email})"


class Comment(models.Model):
    creator = models.ForeignKey(Profile, on_delete=models.CASCADE)
    outing = models.ForeignKey(Outing, on_delete=models.CASCADE, related_name="comments")
    content = models.TextField("Comment", blank=True)   
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.content
