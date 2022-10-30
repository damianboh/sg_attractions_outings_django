from django.conf import settings
from external_api.tourism_hub_client import TourismHubClient

# Create TourismHubClient instance by getting API KEY stored in settings
def get_client_from_settings():    
    return TourismHubClient(settings.TOURISM_HUB_API_KEY)
