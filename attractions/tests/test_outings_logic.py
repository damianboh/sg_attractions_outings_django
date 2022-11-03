from django.test import TestCase
from django.urls import reverse

import datetime

from django.test import TestCase
from django.utils import timezone

from attractions.models.attractions import Attraction
from attractions.models.outings import Outing, OutingInvitation
from custom_auth.models import User
from attractions.forms import OutingForm

from django.db.models import signals
        

class OutingDetailViewTests(TestCase):
    """ 
    Only creator and invitee should be able to view outing details.
    If outing is in the past, submit_invite form will not be present.
    """
    def setUp(self):
        signals.post_save.disconnect(sender=OutingInvitation, dispatch_uid="invitation_create") # do not send emails during testing
        signals.pre_save.disconnect(sender=OutingInvitation, dispatch_uid="invitation_update") # do not send emails during testing
        
        self.u_creator = User.objects.create(name="Creator", email="creator@example.com", password="password") # creator of outing
        self.u_invitee = User.objects.create(name="Invitee", email="invitee@example.com") # invitee of outing
        self.u_other = User.objects.create(name="Other", email="other@example.com") # neither creator nor invitee
        
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
        
        self.outing_detail_link = reverse("outing_detail", args=[self.outing.pk])
   
    # creator of outing can access outing details page
    def test_creator_can_access_outing_detail(self):
        self.client.force_login(self.u_creator)
        response = self.client.get(self.outing_detail_link)
        self.assertEqual(response.status_code, 200)

    # outing invitee can access outing details page
    def test_creator_can_access_outing_detail(self):
        self.client.force_login(self.u_invitee)
        response = self.client.get(self.outing_detail_link)
        self.assertEqual(response.status_code, 200)
    
    # non-creator and non-invitee cannot access outing details page
    def test_creator_can_access_outing_detail(self):
        self.client.force_login(self.u_other)
        response = self.client.get(self.outing_detail_link)
        self.assertEqual(response.status_code, 403) # not authorized
        
    # submit_invite form will not be present in past outing
    # will display a message saying outing is in the past
    def test_past_outing_detail(self):
        self.client.force_login(self.u_creator)
        past_outing = Outing.objects.create(
            attraction = self.attraction, 
            start_time = timezone.now() - datetime.timedelta(days=1),
            creator = self.u_creator.profile,
            )
         
        past_outing_detail_link = reverse("outing_detail", args=[past_outing.pk])
        response = self.client.get(past_outing_detail_link)
        self.assertTrue('This outing is in the past, and invites cannot be added.' in response.content.decode())
        self.assertFalse('name="submit_invite"' in response.content.decode()) # form with submit_invite button not in page
        
    # submit_invite form will be present in future outing
    def test_future_outing_detail(self):
        self.client.force_login(self.u_creator)
        response = self.client.get(self.outing_detail_link)
        self.assertFalse('This outing is in the past, and invites cannot be added.' in response.content.decode())
        self.assertTrue('name="submit_invite"' in response.content.decode()) # form with submit_invite button is in page
        

class OutingInvitationFormTests(TestCase):
    """
    Creator and invitee (user that is already invited) cannot be invited to outings.
    Non-user cannot be invited.
    Only user who has not been invited can be invited.
    """
    def setUp(self):
        signals.post_save.disconnect(sender=OutingInvitation, dispatch_uid="invitation_create") # do not send emails during testing
        signals.pre_save.disconnect(sender=OutingInvitation, dispatch_uid="invitation_update") # do not send emails during testing
        
        self.u_creator = User.objects.create(name="Creator", email="creator@example.com", password="password") # creator of outing
        self.u_invitee = User.objects.create(name="Invitee", email="invitee@example.com") # invitee of outing
        self.u_other = User.objects.create(name="Other", email="other@example.com") # neither creator nor invitee
        
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
        
        self.outing_detail_link = reverse("outing_detail", args=[self.outing.pk])
        self.client.force_login(self.u_creator)
    
    # invitee cannot be invited to outing again
    def test_invite_invitee_to_outing(self):
        email = self.u_invitee.email # simulate submitting invitee email through invite form        
        response = self.client.post(self.outing_detail_link, {"submit_invite": "Invite", "email": email})
        self.assertTrue('That user is the creator or already invited.' in response.content.decode())
     
    # creator cannot be invited to outing
    def test_invite_creator_to_outing(self):
        email = self.u_creator.email # simulate submitting creator email through invite form
        response = self.client.post(self.outing_detail_link, {"submit_invite": "Invite", "email": email})
        self.assertTrue('That user is the creator or already invited.' in response.content.decode()) 
        
    # other user can be invited to outing
    def test_invite_other_user_to_outing(self):
        email = self.u_other.email # simulate submitting another user's email through invite form      
        response = self.client.post(self.outing_detail_link, {"submit_invite": "Invite", "email": email})
        self.assertFalse('User with email address &#x27;' + email + '&#x27; was not found.' in response.content.decode())         
        # also assert that OutingInvitation has been created for profile of other user
        self.assertTrue(OutingInvitation.objects.get(invitee=self.u_other.profile))
        
    # non-user cannot be invited to outing
    def test_invite_non_user_to_outing(self):
        email = "not_a_user@example.com" # simulate submitting email of non user through invite form
        response = self.client.post(self.outing_detail_link, {"submit_invite": "Invite", "email": email})
        self.assertTrue('User with email address &#x27;' + email + '&#x27; was not found.' in response.content.decode())   
    

class OutingFormTests(TestCase):
    """
    Cannot create outing if start time is in the past.
    """    
    def test_outing_start_time_past(self):
        form = OutingForm(data={"start_time": timezone.now() - datetime.timedelta(days=1)})    
        self.assertFormError(form, "start_time", ["Unable to create outing as start time is in the past."])      
            
    def test_outing_start_time_future(self):
        form = OutingForm(data={"start_time": timezone.now() + datetime.timedelta(days=1)})            
        self.assertTrue(form.is_valid())
        



  