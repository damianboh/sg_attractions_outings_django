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
        # check if corresponding profile is created from above user
        profile = Profile.objects.get(name=self.name)
        self.assertEqual(profile.email, self.email)
        
    def test_user_updated_when_profile_updated(self):
        profile = Profile.objects.get(name=self.name)
        updated_name = "name1_updated"
        profile.name = updated_name
        profile.save()
        
        user = User.objects.all().first()                
        self.assertEqual(user.name, updated_name)

    def test_user_deleted_when_profile_deleted(self):
        profile = Profile.objects.get(name=self.name)
        profile.delete()

        # check that does not exist is raised i.e. user has been deleted
        with self.assertRaises(User.DoesNotExist): 
            User.objects.get(name=self.name)
  
        