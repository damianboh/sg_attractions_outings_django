from celery import shared_task
from attractions import email_notifications
from attractions.models import OutingInvitation
# from attractions import tourism_hub_integrated

# all email_notifications functions are converted to async tasks

@shared_task
def send_invitation(mni_pk):
    email_notifications.send_invitation(OutingInvitation.objects.get(pk=mni_pk))


@shared_task
def send_attendance_change(mni_pk, is_attending):
    email_notifications.send_attendance_change(
        OutingInvitation.objects.get(pk=mni_pk), is_attending)


@shared_task
def notify_of_starting_soon():
    email_notifications.notify_of_starting_soon()
	

# can implement in future
# @shared_task
# def search_and_save(search):
#     return tourism_hub_integrated.search_and_save(search)