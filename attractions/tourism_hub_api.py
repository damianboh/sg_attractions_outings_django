import logging
import re
from datetime import timedelta

from django.utils.timezone import now

from .models.attractions import Tag, SearchTerm, Attraction
from external_api.django_client import get_client_from_settings

logger = logging.getLogger(__name__)

# Save list of tag names into separate Tag objects in DB
def get_or_create_tags(tag_names):
    for tag_name in tag_names:
        tag, created = Tag.objects.get_or_create(name=tag_name)
        yield tag

# Get full details of movie from Tourism Hub API, save it to DB.
# Only happens when attraction does not have full_record yet
# i.e. nobody has clicked on the movie to request for full details before
def fill_attraction_details(attraction):
    if movie.is_full_record:
        logger.warning(
            "'%s' is already a full record.",
            movie.title,
        )
        return
    tourism_hub_client = get_client_from_settings()
    movie_details = tourism_hub_client.get_by_uuid(attraction.uuid)
    movie.title = movie_details.title
    movie.year = movie_details.year
    movie.plot = movie_details.plot
    movie.runtime_minutes = movie_details.runtime_minutes
    movie.genres.clear()
    for genre in get_or_create_genres(movie_details.genres):
        movie.genres.add(genre)
    movie.is_full_record = True
    movie.save()


def search_and_save(search):
    """
    Perform a search for search_term against the API, but only if it hasn't been searched in the past 24 hours. Save
    each result to the local DB as a partial record.
    """
    # Replace multiple spaces with single spaces, and lowercase the search
    normalized_search_term = re.sub(r"\s+", " ", search.lower())

    search_term, created = SearchTerm.objects.get_or_create(term=normalized_search_term)

    if not created and (search_term.last_search > now() - timedelta(days=1)): # change to was searched recently function using tutorial 2
        # Don't search as it has been searched recently
        logger.warning(
            "Search for '%s' was performed in the past 24 hours so not searching again.",
            normalized_search_term,
        )
        return

    omdb_client = get_client_from_settings()

    for omdb_movie in omdb_client.search(search):
        logger.info("Saving movie: '%s' / '%s'", omdb_movie.title, omdb_movie.imdb_id)
        movie, created = Movie.objects.get_or_create(
            imdb_id=omdb_movie.imdb_id,
            defaults={
                "title": omdb_movie.title,
                "year": omdb_movie.year,
            },
        )

        if created:
            logger.info("Movie created: '%s'", movie.title)

    search_term.save()
