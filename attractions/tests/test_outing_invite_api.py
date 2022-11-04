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


class OutingInviteAPITests(TestCase):
    """ 
    Only creator of outing can invite people using API.
    Even invitee cannot invite others.
    """
    def setUp(self):
        signals.post_save.disconnect(sender=OutingInvitation, dispatch_uid="invitation_create") # do not send emails during testing
        signals.pre_save.disconnect(sender=OutingInvitation, dispatch_uid="invitation_update") # do not send emails during testing
        
        self.u_creator = User.objects.create(name="Creator", email="creator@example.com") # creator of outing
        self.u_invitee = User.objects.create(name="Invitee", email="invitee@example.com") # invitee of 2 outings
        self.u_other = User.objects.create(name="Other", email="other@example.com") # neither creator nor invitee
        
        attraction = Attraction.objects.create(name="Some Attraction", uuid="123")
        
        self.outing = Outing.objects.create(
            attraction = attraction, 
            start_time = timezone.now() + datetime.timedelta(days=3),
            creator = self.u_creator.profile,
            )

        outing_id = str(self.outing.id) # for use in API endpoint later
        self.invite_endpoint = "/api/v1/outings/" + outing_id + "/invite/"
         
        outing_invitation = OutingInvitation.objects.create(
            outing = self.outing,
            invitee =  self.u_invitee.profile,
            )

        self.outing_invitation_endpoint = "/api/v1/outing_invitations/" + str(outing_invitation.id) + "/"

        self.token_creator = Token.objects.create(user=self.u_creator)
        self.token_invitee = Token.objects.create(user=self.u_invitee)
        self.token_other = Token.objects.create(user=self.u_other)

        self.client = APIClient()

    # only POST method is allowed for /outings/{id}/invite/
    def test_creator_invite_create(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token_creator.key)        
        resp = self.client.get(self.invite_endpoint)        
        data = resp.json()
        self.assertEqual(data['detail'], 'Method "GET" not allowed.')

    # creator of outing can invite 'u_other' user via /outings/{id}/invite/
    def test_creator_invite(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token_creator.key)        
        self.client.post(self.invite_endpoint, {"invitee": self.u_other.email})   
        # check invitiation created for 'u_other'     
        self.assertTrue(OutingInvitation.objects.filter(invitee=self.u_other.profile))

    # invitee of outing cannot invite another user (only creator can)
    def test_invitee_invite(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token_invitee.key)        
        self.client.post(self.invite_endpoint, {"invitee": self.u_other.email})   
        # check invitiation NOT created for 'u_other'     
        self.assertFalse(OutingInvitation.objects.filter(invitee=self.u_other.profile))

    # other user cannot invite another user (only creator can)
    def test_other_invite(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token_other.key)        
        self.client.post(self.invite_endpoint, {"invitee": self.u_other.email})   
        # check invitiation NOT created for 'u_other'     
        self.assertFalse(OutingInvitation.objects.filter(invitee=self.u_other.profile))

    # an invitee cannot be invited again
    def test_creator_invite_invitee_again(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token_creator.key)        
        resp = self.client.post(self.invite_endpoint, {"invitee": self.u_invitee.email})   
        data = resp.json()
        self.assertEqual(data['invitee'], [self.u_invitee.email + ' has already been invited to this outing.'])
        # number of OutingInvitation objects with invitee = u_invitee should still be 1
        self.assertEqual(len(OutingInvitation.objects.filter(invitee=self.u_invitee.profile)), 1)
