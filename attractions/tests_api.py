from datetime import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from pytz import UTC
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

import datetime

from .models.attractions import Attraction, Tag
from .models.outings import Outing, OutingInvitation
from custom_auth.models import User, Profile

from django.db.models import signals
from django.db.models.signals import pre_save, post_save

from rest_framework.authtoken.models import Token


class AttractionsAPITests(TestCase):
    """
    Test API attractions list endpoint.
    """
    def setUp(self):
        signals.post_save.disconnect(sender=OutingInvitation, dispatch_uid="invitation_create") # do not send emails during testing
        signals.pre_save.disconnect(sender=OutingInvitation, dispatch_uid="invitation_update") # do not send emails during testing
        
        self.u1 = User.objects.create(name="Adam", email="adam@example.com") 
        self.u2 = User.objects.create(name="Bob", email="bob@example.com")
        
        tag1 = Tag.objects.create(name='Leisure')
        tag2 = Tag.objects.create(name='Nature')
        
        attraction1 = Attraction.objects.create(
                name="Botanic Gardens", 
                attraction_type="Park and Gardens",
                uuid="123",
                summary="A nice garden.",
                is_full_record=True,
                full_description='This is a really nice garden.',
                nearest_station='Botanic Gardens MRT',
                website_url='http://garden.com',
                admission_info='Free',
                map_url='http://some.url',
                )        
        attraction1.tags.add(tag1)
        attraction1.tags.add(tag2)
        attraction1.saved_by.add(self.u1.profile)
        attraction1.saved_by.add(self.u2.profile)
        
        attraction2 =  Attraction.objects.create(
                name="Art Museum", 
                attraction_type="Museums",
                uuid="345",
                summary="A nice museum.",
                is_full_record=True,
                full_description='This is a really nice museum.',
                nearest_station='Museum MRT',
                website_url='http://museum.com',
                admission_info='$2 for adults',
                map_url='http://some.url',
                )        
        attraction2.tags.add(tag1)
        attraction2.saved_by.add(self.u2.profile)    

        attractions = [attraction1, attraction2]        
        self.attractions_lookup = {a.uuid: a for a in attractions}

        # override Django test client with API client given by DRF
        self.client = APIClient()
        token = Token.objects.create(user=self.u1)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + token.key) # simulate login of user u1
        
    def test_attraction_list(self):
        resp = self.client.get("/api/v1/attractions/")
        data = resp.json()["results"] # from pagination results
        self.assertEqual(len(data), 2)

        # see if attractions list returned by API is same as attractions created earlier
        for attraction_dict in data:
            attraction_obj = self.attractions_lookup[attraction_dict["uuid"]]
            attraction_obj_tags = []
            for tag in attraction_obj.tags.all():
                attraction_obj_tags.append(tag.name)
            attraction_obj_saved_by = []
            for saved_by in attraction_obj.saved_by.all():
                attraction_obj_saved_by.append(saved_by.email)
            self.assertEqual(attraction_obj.name, attraction_dict["name"])
            self.assertEqual(attraction_obj.attraction_type, attraction_dict["attraction_type"])
            self.assertEqual(attraction_obj.summary, attraction_dict["summary"])
            self.assertEqual(attraction_obj.is_full_record, attraction_dict["is_full_record"])
            self.assertEqual(attraction_obj.full_description, attraction_dict["full_description"])
            self.assertEqual(attraction_obj.nearest_station, attraction_dict["nearest_station"])
            self.assertEqual(attraction_obj.website_url, attraction_dict["website_url"])
            self.assertEqual(attraction_obj.admission_info, attraction_dict["admission_info"]) 
            self.assertEqual(attraction_obj_tags, attraction_dict["tags"]) 
            self.assertEqual(attraction_obj_saved_by, attraction_dict["saved_by"]) 


class OutingAPITests(TestCase):
    """ 
    Only creator and invitee should be able to view outing details.
    If outing is in the past, submit_invite form will not be present.
    """
    def setUp(self):
        signals.post_save.disconnect(sender=OutingInvitation, dispatch_uid="invitation_create") # do not send emails during testing
        signals.pre_save.disconnect(sender=OutingInvitation, dispatch_uid="invitation_update") # do not send emails during testing
        
        self.u_creator = User.objects.create(name="Creator", email="creator@example.com", password="password") # creator of outing
        self.u_invitee = User.objects.create(name="Invitee", email="invitee@example.com") # invitee of 2 outings
        self.u_other = User.objects.create(name="Other", email="other@example.com") # neither creator nor invitee
        
        attraction = Attraction.objects.create(name="Some Attraction", uuid="123")
        
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

        self.client = APIClient()

        
    def test_invitee_outing_list(self):
        token = Token.objects.create(user=self.u_invitee)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + token.key)
        resp = self.client.get("/api/v1/outings/")

        data = resp.json() # from pagination results
        print(data)
        #self.assertEqual(len(data), 2)
        

        # see if attractions list returned by API is same as attractions created earlier
        for attraction_dict in data:
            attraction_obj = self.attractions_lookup[attraction_dict["uuid"]]
            attraction_obj_tags = []
            for tag in attraction_obj.tags.all():
                attraction_obj_tags.append(tag.name)
            attraction_obj_saved_by = []
            for saved_by in attraction_obj.saved_by.all():
                attraction_obj_saved_by.append(saved_by.email)
            self.assertEqual(attraction_obj.name, attraction_dict["name"])
            self.assertEqual(attraction_obj.attraction_type, attraction_dict["attraction_type"])
            self.assertEqual(attraction_obj.summary, attraction_dict["summary"])
            self.assertEqual(attraction_obj.is_full_record, attraction_dict["is_full_record"])
            self.assertEqual(attraction_obj.full_description, attraction_dict["full_description"])
            self.assertEqual(attraction_obj.nearest_station, attraction_dict["nearest_station"])
            self.assertEqual(attraction_obj.website_url, attraction_dict["website_url"])
            self.assertEqual(attraction_obj.admission_info, attraction_dict["admission_info"]) 
            self.assertEqual(attraction_obj_tags, attraction_dict["tags"]) 
            self.assertEqual(attraction_obj_saved_by, attraction_dict["saved_by"]) 
