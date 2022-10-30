from datetime import timedelta
from django.contrib.auth import get_user_model
from django.db import models
from .attractions import Attraction

UserModel = get_user_model() # from custom user model

# A creator creates outing for a particular attracton at a particular time
class Outing(models.Model):
    class Meta:
        ordering = ["start_time"]

    attraction = models.ForeignKey(Attraction, on_delete=models.PROTECT)
    start_time = models.DateTimeField()
    creator = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    start_notification_sent = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} by {self.creator.name} ({self.creator.email})"


class OutingInvitation(models.Model):
    class Meta:
        unique_together = [("invitee", "outing")]

    outing = models.ForeignKey(Outing, on_delete=models.CASCADE, related_name="invites")
    invitee = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    attendance_confirmed = models.BooleanField(default=False)
    is_attending = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.outing} / {self.invitee.name} ({self.invitee.email})"
