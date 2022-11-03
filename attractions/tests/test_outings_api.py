from datetime import datetime

from django.test import TestCase
from django.utils import timezone

from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

import datetime

from attractions.models.attractions import Attraction, Tag
from attractions.models.outings import Outing, OutingInvitation
from custom_auth.models import User

from django.db.models import signals

from rest_framework.authtoken.models import Token

class OutingsAPITests(TestCase):
    """ 
    Only creator and invitee should be able to view outing details.
    If outing is in the past, submit_invite form will not be present.
    """
    def setUp(self):
        signals.post_save.disconnect(sender=OutingInvitation, dispatch_uid="invitation_create") # do not send emails during testing
        signals.pre_save.disconnect(sender=OutingInvitation, dispatch_uid="invitation_update") # do not send emails during testing
        
        self.u_creator = User.objects.create(name="Creator", email="creator@example.com") # creator of outing
        self.u_invitee = User.objects.create(name="Invitee", email="invitee@example.com") # invitee of 2 outings
        self.u_other = User.objects.create(name="Other", email="other@example.com") # neither creator nor invitee
        
        attraction = Attraction.objects.create(name="Some Attraction", uuid="123")
        
        # u_invitee invited to 2 outings
        self.invited_outings = [
            Outing.objects.create(
                attraction = attraction, 
                start_time = timezone.now() + datetime.timedelta(days=1),
                creator = self.u_creator.profile,
                ),
            
            Outing.objects.create(
                attraction = attraction, 
                start_time = timezone.now() + datetime.timedelta(days=2),
                creator = self.u_creator.profile,
                )
        ]

        self.outing_not_invited = Outing.objects.create(
            attraction = attraction, 
            start_time = timezone.now() + datetime.timedelta(days=3),
            creator = self.u_creator.profile,
            )
         
        for outing in self.invited_outings:
            OutingInvitation.objects.create(
                outing = outing,
                invitee =  self.u_invitee.profile,
                )

        self.token_creator = Token.objects.create(user=self.u_creator)
        self.token_invitee = Token.objects.create(user=self.u_invitee)
        self.token_other = Token.objects.create(user=self.u_other)

        self.client = APIClient()

    # creator should see all 3 created outings
    def test_creator_outing_list(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token_creator.key)
        resp = self.client.get("/api/v1/outings/")        
        data = resp.json()['results'] 

        self.assertEqual(len(data), 3) # all 3 created outings

        # the 3 outing objects created earlier match the outings from api
        for i, outing in enumerate(Outing.objects.all()):            
            self.assertEqual(data[i]['id'], str(outing.id)) 
         
    # invitee cannot see any of the outings
    def test_invitee_outing_list(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token_invitee.key)
        resp = self.client.get("/api/v1/outings/")        
        data = resp.json()['results']         
        self.assertEqual(len(data), 0) # no outing returned

    # using another endpoint outings/invited/, invitee can see the 2 invited outings
    def test_invitee_outing_list(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token_invitee.key)
        resp = self.client.get("/api/v1/outings/invited/")        
        data = resp.json()['results'] 
        self.assertEqual(len(data), 2) # both invited outings returned

        # the outing IDs of invited outings objects and outing IDs of API data returned are the same
        for outing in data:
            for outingInvitationObg in OutingInvitation.objects.filter(outing=outing['id']):
                self.assertTrue(outingInvitationObg.outing.id, outing['id'])

    # another user (neither creator nor invitee in any outing)
    # would not see any outing in both outings and outings/invited/ endpoints
    def test_other_user_outing_list(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token_other.key)
        resp = self.client.get("/api/v1/outings/")        
        data = resp.json()['results'] 
        self.assertEqual(len(data), 0)

        resp = self.client.get("/api/v1/outings/invited/")        
        data_invited = resp.json()['results'] 
        self.assertEqual(len(data_invited), 0)
            

