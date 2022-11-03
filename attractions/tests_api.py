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
        resp = self.client.get("/api/v1/attractions/attractions/")
        # data = resp.json()
        data = resp.json()["results"] # from pagination results
        self.assertEqual(len(data), 2)
        
        print(data)

        # see if attractions list returned by API is same as attractions created earlier
        for post_dict in data:
            post_obj = self.attractions_lookup[post_dict["uuid"]]
            self.assertEqual(post_obj.name, post_dict["name"])
            self.assertEqual(post_obj.attraction_type, post_dict["attraction_type"])
            self.assertEqual(post_obj.summary, post_dict["summary"])
            self.assertEqual(post_obj.is_full_record, post_dict["is_full_record"])
            self.assertEqual(post_obj.full_description, post_dict["full_description"])
            self.assertEqual(post_obj.nearest_station, post_dict["nearest_station"])
            self.assertEqual(post_obj.website_url, post_dict["website_url"])
            self.assertEqual(post_obj.admission_info, post_dict["admission_info"]) 
 