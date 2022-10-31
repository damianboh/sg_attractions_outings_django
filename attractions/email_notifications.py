from datetime import timedelta
from urllib.parse import urljoin

from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone

from attractions.models import Outing


def send_invitation(outing_invitation):
    # email subject and body contents
    # e.g. template tags like {{outing}} in email will be rendered accordingly
    subject = render_to_string(
        "attractions/email_notifications/invitation_subject.txt",
        {"outing": outing_invitation.outing},
    )

    outing_path = reverse(
        "outing_detail", args=(outing_invitation.outing.pk,)
    )

    body = render_to_string(
        "attractions/email_notifications/invitation_body.txt",
        {
            "creator": outing_invitation.outing.creator,
            "outing": outing_invitation.outing,
            "outing_url": urljoin(settings.BASE_URL, outing_path),
        },
    )

    send_mail(
        subject,
        body,
        None,
        [outing_invitation.invitee.email],
    )


# let creator know when users update their attendance
def send_attendance_change(outing_invitation, is_attending):
    subject = render_to_string(
        "attractions/email_notifications/attendance_update_subject.txt",
        {
            "outing": outing_invitation.outing,
            "outing_invitation": outing_invitation,
        },
    )

    outing_path = reverse(
        "outing_detail", args=(outing_invitation.outing.pk,)
    )

    body = render_to_string(
        "attractions/email_notifications/attendance_update_body.txt",
        {
            "is_attending": is_attending,
            "outing_invitation": outing_invitation,
            "outing": outing_invitation.movie_night,
            "outing_url": urljoin(settings.BASE_URL, outing_path),
        },
    )

    send_mail(
        subject,
        body,
        None,
        [outing_invitation.outing.creator.email],
    )


# let all users of an outing know if the outing is starting soon
def send_starting_notification(outing):
    subject = render_to_string(
        "attractions/email_notifications/starting_subject.txt",
        {"outing": outing},
    )

    outing_path = reverse("outing_detail", args=(outing.pk,))

    body = render_to_string(
        "attractions/email_notifications/starting_body.txt",
        {
            "outing": outing,
            "outing_url": urljoin(settings.BASE_URL, outing_path),
        },
    )

    to_emails = [
        invite.invitee.email for invite in outing.invites.filter(is_attending=True)
    ]
    to_emails.append(outing.creator.email)

    send_mail(
        subject,
        body,
        None,
        to_emails,
    )
    outing.start_notification_sent = True
    outing.save()


def notify_of_starting_soon():
    # Find all outings that start in the next 30 minutes, or before, if we haven't notified
    start_before = timezone.now() + timedelta(minutes=30)

    # all outings that are starting soon but not notified yet
    outings = Outing.objects.filter(
        start_time__lte=start_before, start_notification_sent=False
    )

    for outing in outings:
        send_starting_notification(outing)
