from django.test import TestCase
import datetime
from .models import User, Profile


class UserAndProfileSyncTests(TestCase):
    """
    This test is for validating the following:
    - When user is created, corresponding profile is created with same name and email.
    - When profile is updated, corresponding user is updated to have the same fields.
    - When profile is deleted, corresponding user is also deleted.
    The above are set up in signals.
    """
    def setUp(self):
        self.name = "name1"
        self.email = "user1@example.com"
        User.objects.create(name=self.name, email=self.email)
        
   
    def test_profile_created_when_user_created(self):
        profile = Profile.objects.all().first()
        self.assertEqual(profile.name, self.name)
        self.assertEqual(profile.email, self.email)
        
    def test_user_updated_when_profile_updated(self):
        profile = Profile.objects.all().first()
        updated_name = "name1_updated"
        #updated_email = "updated@email.com"
        profile.name = updated_name
        #profile.email = updated_email
        profile.save()
        
        user = User.objects.all().first()
        
        print(user)
        
        self.assertEqual(user.name, updated_name)
  
        