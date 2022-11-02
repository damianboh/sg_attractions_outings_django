from django.test import TestCase
from django.urls import reverse

import datetime

from django.test import TestCase
from django.utils import timezone

from .models.attractions import SearchTerm, Attraction
from .models.outings import Outing, OutingInvitation
from custom_auth.models import User, Profile
from .forms import InviteeForm, OutingForm

from django.db.models import signals
from django.db.models.signals import pre_save, post_save

class SearchTermModelTests(TestCase):    
    def test_was_searched_recently_with_old_search_term(self):
        # 1 second before 24 hours ago
        time = timezone.now() - datetime.timedelta(days=1, seconds=1) 
        # cannot use SearchTerm.objects.create as auto now is true and it will be created with current time
        old_term = SearchTerm(last_search_date=time) 
        self.assertFalse(old_term.was_searched_recently())

    def test_was_published_recently_with_recent_search_term(self):
        # 1 second after 24 hours ago
        time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59) 
        recent_term = SearchTerm(last_search_date=time)
        self.assertTrue(recent_term.was_searched_recently())
        

class OutingInvitationFormTests(TestCase):
    def setUp(self):
        signals.post_save.disconnect(sender=OutingInvitation, dispatch_uid="invitation_create") # do not send emails during testing
        signals.pre_save.disconnect(sender=OutingInvitation, dispatch_uid="invitation_update") # do not send emails during testing
        
        User.objects.create(name="Creator", email="creator@example.com") # creator of outing
        User.objects.create(name="Invitee", email="invitee@example.com") # invitee of outing
        User.objects.create(name="Other", email="other@example.com") # neither creator nor invitee
        
        self.attraction = Attraction.objects.create(name="Some Attraction")
        
        self.outing = Outing.objects.create(
            attraction = self.attraction, 
            start_time = timezone.now() + datetime.timedelta(days=1),
            creator = Profile.objects.get(email="creator@example.com"),
            )
         
        OutingInvitation.objects.create(
            outing = self.outing,
             # signals will create corresponding Profiles after User is created above
            invitee = Profile.objects.get(email="invitee@example.com"),
            )
   
    def test_outing_invitation_invitee_not_user(self):
        form = InviteeForm(data={"email": "no_such_user@example.com"})
        self.assertTrue(form.errors["email"]) # error in email field
        # print(form.errors["email"])
        
    def test_outing_invitation_invitee_is_user(self):
        form = InviteeForm(data={"email": "other@example.com"})
        self.assertFalse(form.errors) # no error
        
    def test_outing_invitation_invitee_has_creator_email(self):
        outing_detail_link = reverse("outing_detail", args=[self.outing.pk])
        response = self.client.post(outing_detail_link, data={"email": "creator@example.com"})
        print(response.content)
        

class OutingFormTests(TestCase):
         
    def test_outing_start_time_past(self):
        form = OutingForm(data={"start_time": timezone.now() - datetime.timedelta(days=1)})            
        self.assertTrue(form.errors["start_time"])
        
        
    def test_outing_start_time_future(self):
        form = OutingForm(data={"start_time": timezone.now() + datetime.timedelta(days=1)})            
        self.assertFalse(form.errors)
        



  