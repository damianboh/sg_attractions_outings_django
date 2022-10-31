"""
Client for making requests to the Singapore Tourism and Information Services Hub API.
Results will be returned in a Python TourismHubAttraction Object.
Client is standalone and decoupled from Django App, Django integrations are included in other files.
HTML is formatted with allowed text and url links are cleaned.
"""

import logging
import requests
import re
from html_sanitizer import Sanitizer

logger = logging.getLogger(__name__)

TOURISM_HUB_API_URL = "https://api.stb.gov.sg/content/attractions/v2/search"

sanitizer = Sanitizer()

class TourismHubAttraction:
    """A simple class to represent attraction data coming back 
    from Tourism Hub API and transform to Python object."""
    
    # Data is the raw JSON/dict returned from Tourism Hub
    def __init__(self, data):        
        self.data = data
    
    # Some keys are only in the detailed response that should only be loaded
    # when user wants to view details of attraction
    # raise an exception if the key is not found.
    def check_for_detail_data_key(self, key):
        if key not in self.data:
            raise AttributeError(f"{key} is not in data, please make sure this is a detailed response.")

    @property
    def uuid(self):
        return self.data["uuid"]

    @property
    def name(self):
        return self.data["name"]
    
    # This returns a list
    @property
    def attraction_type(self):
        return self.data["type"]

    @property
    def summary(self):
        # summary is html code that should be sanitized
        return sanitizer.sanitize(self.data["description"])

    
    # Values below will only return when user clicks to see attraction in detail

    @property
    def full_description(self):
        self.check_for_detail_data_key("body")
        # full_description is html code that should be sanitized
        return sanitizer.sanitize(self.data["body"])

    @property
    def tags(self): 
        # Note: This is a list
        self.check_for_detail_data_key("tags")
        return self.data["tags"]
    
    @property
    def nearest_station(self):
        self.check_for_detail_data_key("nearestMrtStation")
        return self.data["nearestMrtStation"]
    
    @property
    def website_url(self):
        self.check_for_detail_data_key("officialWebsite")        
        return format_url(self.data["officialWebsite"])

    # This returns admission rate of adults/child etc.
    @property
    def admission_info(self):
        self.check_for_detail_data_key("admissionInfo")
        return self.data["admissionInfo"]
    
    # Convert location latitude and longitude to Google Map URL that can be embedded in iframe
    @property
    def map_url(self): 
        self.check_for_detail_data_key("location")
        latitude = self.data["location"]["latitude"]
        longitude = self.data["location"]["longitude"]
        # check that latitude and longitude are floats to prevent malicious html from being injected
        if ((isinstance(latitude, float)) & (isinstance(longitude, float))): 
            return "https://maps.google.com/maps?q=" + str(latitude) + "," + str(longitude) + "&hl=es;z=14&amp;output=embed"
        else:
            return ""


class TourismHubClient:
    # Initialize with API key
    def __init__(self, api_key):
        self.api_key = api_key

    # Make a GET request to the Singapore Tourism Hub API with the self.api_key parameter.
    def make_request(self, params):
        resp = requests.get(TOURISM_HUB_API_URL, 
                        headers={'Content-Type': 'application/json', 
                        'X-API-Key': self.api_key}, 
                        params=params) # search query params
        resp.raise_for_status()
        return resp

    # Get a single attraction by its Tourism Hub API UUID
    def get_by_uuid(self, uuid):
        logger.info("Fetching detail for UUID %s", uuid)
        resp = self.make_request({"searchValues": uuid, "searchType": "uuids"})
        return TourismHubAttraction(resp.json()["data"][0])

    # Search for attractions by name, all matching attractions are returned in generator
    def search(self, search):
        offset = 0
        seen_results = 0
        total_results = 0

        logger.info("Performing a search for '%s'", search)

        # Iterate across all results in every page untill all results are seen
        # Yields generator object
        while True:        
            resp = self.make_request({"searchValues": search, 
                                      "searchType": "keyword", 
                                      "limit":"50", 
                                      "offset":offset})
            resp_body = resp.json()
            total_results = resp_body['totalRecords']
            retrieved_results = resp_body['retrievedRecords']
            seen_results += retrieved_results # total results fetched
            logger.info("Total results fetched: %d", seen_results)
            
            for attraction in resp_body["data"]:
                yield TourismHubAttraction(attraction)    
            
            if seen_results >= total_results: # if all results are fetched, stop
                break

            offset += 50 # since API limit is 50, each page has 50 results   


def format_url(url):
    if url == "":
        return ""
    if not re.match('(?:http|ftp|https)://', url):
        return 'https://{}'.format(url)
    return url    