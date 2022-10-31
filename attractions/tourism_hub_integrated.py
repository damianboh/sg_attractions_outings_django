import logging
import re
from datetime import timedelta

from django.utils.timezone import now
import requests

from .models.attractions import Tag, SearchTerm, Attraction
from external_api.django_client import get_client_from_settings

logger = logging.getLogger(__name__)


def get_or_create_tags(tag_names):
    """
    Save list of tag names into separate Tag objects in DB
    """
    for tag_name in tag_names:
        tag, created = Tag.objects.get_or_create(name=tag_name)
        yield tag

def fill_attraction_details(attraction):
    """
    Get full details of attraction from Tourism Hub API, save it to DB.
    Only happens when attraction does not have full_record yet
    i.e. nobody has clicked on the attraction to request for full details before
    attraction here is an object from DB
    """
    if attraction.is_full_record:
        logger.warning(
            "'%s' is already a full record.",
            attraction.name,
        )
        return

    tourism_hub_client = get_client_from_settings()

    try:
        attraction_from_api = tourism_hub_client.get_by_uuid(attraction.uuid)
        attraction.name = attraction_from_api.name
        attraction.attraction_type = attraction_from_api.attraction_type
        attraction.summary = attraction_from_api.summary
        attraction.full_description = attraction_from_api.full_description
        attraction.nearest_station = attraction_from_api.nearest_station
        attraction.website_url = attraction_from_api.website_url
        attraction.admission_info = attraction_from_api.admission_info
        attraction.map_url = attraction_from_api.map_url
        attraction.tags.clear()

        for tag in get_or_create_tags(attraction_from_api.tags):
            attraction.tags.add(tag)

        attraction.is_full_record = True # full details has been updated
        attraction.save()

    except requests.exceptions.HTTPError:
        logger.error("Failed to fetch attractions by UUID from API.")



def search_and_save(search):
    """
    Perform a search against Tourism Hub API, 
    only if it hasn't been searched recently (past 24 hours). 
    Save each result to the local DB as a partial record
    i.e only uuid, name, attraction_type, summary is saved
    """
    # Replace multiple spaces with single spaces, and lowercase the search
    normalized_search_term = re.sub(r"\s+", " ", search.lower())

    search_term, created = SearchTerm.objects.get_or_create(term=normalized_search_term)

    if not created and (search_term.was_searched_recently):
        # Don't search as it has been searched recently
        logger.warning(
            "Search for '%s' was performed in the past 24 hours so not searching again.",
            normalized_search_term,
        )
        return

    tourism_hub_client = get_client_from_settings()

    try:

        for attraction_from_api in tourism_hub_client.search(search):
            logger.info("Saving attraction: '%s' / '%s'", attraction_from_api.name, attraction_from_api.uuid)
            attraction, created = Attraction.objects.get_or_create(
                uuid=attraction_from_api.uuid,
                defaults={
                    "name": attraction_from_api.name,
                    "attraction_type": attraction_from_api.attraction_type,
                    "summary": attraction_from_api.summary,
                },
            )

            if created:
                logger.info("Attraction created: '%s'", attraction.name)

        search_term.save()

    except requests.exceptions.HTTPError:

        search_term.delete() # delete instance of search term since search was unsuccessful
        logger.error("Failed to fetch attractions by name from API.")
