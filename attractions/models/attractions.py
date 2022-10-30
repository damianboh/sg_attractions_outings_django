from datetime import timedelta
from django.contrib.auth import get_user_model
from django.db import models
from custom_auth.models import Profile
from django.utils import timezone
from datetime import datetime

UserModel = get_user_model() # from custom user model

# Terms that users used to search are recorded
class SearchTerm(models.Model):
    class Meta:
        ordering = ["last_search_date"]

    term = models.TextField(unique=True)
    last_search_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.term
    
    def was_searched_recently(self):
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.last_search_date <= now


class Tag(models.Model):
    class Meta:
        ordering = ["name"]

    name = models.TextField(unique=True)

    def __str__(self):
        return self.name


class Attraction(models.Model):
    class Meta:
        ordering = ["name"]

    uuid = models.SlugField(unique=True, primary_key=True) # this is lookup field in URL
    name = models.CharField(max_length=300)
    attraction_type = models.CharField(max_length=300, blank=True, null=True)
    summary = models.TextField(blank=True, null=True)

    # Fields below are for full detailed record of attraction
    is_full_record = models.BooleanField(default=False)
    full_description = models.TextField(blank=True, null=True)
    nearest_station = models.TextField(blank=True, null=True)
    website_url = models.CharField(max_length=300, blank=True, null=True)
    admission_info = models.TextField(blank=True, null=True)  
    map_url = models.CharField(max_length=300, blank=True, null=True)
    tags = models.ManyToManyField(Tag, blank=True) 

    saved_by = models.ManyToManyField(Profile, blank=True, related_name='attractions') 

    def __str__(self):
        return f"{self.name}"