from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.views import generic
from django.db.models import Q
from attractions.models.attractions import Attraction
from .models import Profile
from .tourism_hub_integrated import search_and_save, fill_attraction_details

@login_required
def search_attractions(request):
    search_term = ''

    if request.GET.get('search_term'):
        search_term = request.GET.get('search_term')	
        search_and_save(search_term)    
        attractions = Attraction.objects.filter(
            Q(name__icontains=search_term)|
            Q(summary__icontains=search_term)|
            Q(full_description__icontains=search_term)   
            )
        did_search = True

    else:
        attractions = []
        did_search = False  

    return render(
        request,
        "attractions/search.html",
        {
            "page_group": "search",
            "attractions": attractions,
            "did_search": did_search,
        },
    )

@login_required
def attraction_detail(request, uuid):
    attraction = get_object_or_404(Attraction, uuid=uuid)
    fill_attraction_details(attraction)

    context = {"page_group": "search", "attraction": attraction}

    return render(request, "attraction/single_attraction.html", context)