from django.test import TestCase

import datetime

from django.test import TestCase
from django.utils import timezone

from attractions.models.attractions import SearchTerm


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