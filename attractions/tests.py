from http.client import responses
from django.test import TestCase, Client
from django.urls import reverse
import json

import datetime

from django.test import TestCase
from django.utils import timezone

from .models.attractions import SearchTerm, Attraction
from .models.outings import Outing, OutingInvitation
from custom_auth.models import User, Profile
from .forms import InviteeForm, OutingForm

from django.db.models import signals
from django.db.models.signals import pre_save, post_save

from rest_framework.authtoken.models import Token

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
        

class OutingInvitationLogicTests(TestCase):
    def setUp(self):
        signals.post_save.disconnect(sender=OutingInvitation, dispatch_uid="invitation_create") # do not send emails during testing
        signals.pre_save.disconnect(sender=OutingInvitation, dispatch_uid="invitation_update") # do not send emails during testing
        
        self.u_creator = User.objects.create(name="Creator", email="creator@example.com", password="password") # creator of outing
        self.u_invitee = User.objects.create(name="Invitee", email="invitee@example.com") # invitee of outing
        self.u_other = User.objects.create(name="Other", email="other@example.com") # neither creator nor invitee

        self.token_creator = Token.objects.create(user=self.u_creator)
        self.token_invitee = Token.objects.create(user=self.u_invitee)
        self.token_other = Token.objects.create(user=self.u_other)
        
        self.attraction = Attraction.objects.create(name="Some Attraction", uuid="123")
        
        self.outing = Outing.objects.create(
            attraction = self.attraction, 
            start_time = timezone.now() + datetime.timedelta(days=1),
            creator = self.u_creator.profile,
            )
         
        OutingInvitation.objects.create(
            outing = self.outing,
            invitee =  self.u_invitee.profile,
            )
   
    def test_outing_invitation_invitee_not_user(self):
        form = InviteeForm(data={"email": "no_such_user@example.com"})
        self.assertFormError(form, "email", ["User with email address 'no_such_user@example.com' was not found."])   
        
    def test_outing_invitation_invitee_is_user(self):
        form = InviteeForm(data={"email": "other@example.com"})
        self.assertTrue(form.is_valid())

    # creator of outing can access outing details page
    def test_creator_can_access_outing_detail(self):
        self.client.force_login(self.u_creator)
        outing_detail_link = reverse("outing_detail", args=[self.outing.pk])
        response = self.client.get(outing_detail_link)
        self.assertEqual(response.status_code, 200)

    # outing invitee can access outing details page
    def test_creator_can_access_outing_detail(self):
        self.client.force_login(self.u_invitee)
        outing_detail_link = reverse("outing_detail", args=[self.outing.pk])
        response = self.client.get(outing_detail_link)
        self.assertEqual(response.status_code, 200)
    
    # non-creator and non-invitee cannot access outing details page
    def test_creator_can_access_outing_detail(self):
        self.client.force_login(self.u_other)
        outing_detail_link = reverse("outing_detail", args=[self.outing.pk])
        response = self.client.get(outing_detail_link)
        self.assertEqual(response.status_code, 403)
        
    # creator of outing can access outing details page
    def test_creator_can_access_outing_det(self):
        self.client.force_login(self.u_creator)
        outing_detail_link = reverse("outing_detail", args=[self.outing.pk])
        response = self.client.post(outing_detail_link, 
                    json.dumps({"name": "submit_invite", "email": "creator@example.com"}), 
                    content_type="application/json")

        print(response.content)

class OutingFormTests(TestCase):
         
    def test_outing_start_time_past(self):
        form = OutingForm(data={"start_time": timezone.now() - datetime.timedelta(days=1)})    
        self.assertFormError(form, "start_time", ["Unable to create outing as start time is in the past."])      
            
    def test_outing_start_time_future(self):
        form = OutingForm(data={"start_time": timezone.now() + datetime.timedelta(days=1)})            
        self.assertTrue(form.is_valid())
        



  