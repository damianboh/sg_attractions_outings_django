from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.views import generic
from django.db.models import Q
from attractions.models.attractions import Attraction
from attractions.models.outings import Outing
from .forms import OutingForm
from .models import Profile
from .tourism_hub_integrated import search_and_save, fill_attraction_details
from django.contrib import messages

@login_required
def search_attractions(request):
    search_term = ''

    if request.GET.get('search_term'):
        search_term = request.GET.get('search_term')	
        search_and_save(search_term)    
        attractions = Attraction.objects.filter(
            Q(name__icontains=search_term)|
            Q(summary__icontains=search_term)|
            Q(attraction_type__icontains=search_term)
            )
        did_search = True

    else:
        attractions = []
        did_search = False  

    context = {
            "page_group": "search",
            "attractions": attractions,
            "did_search": did_search,
            "search_term": search_term,
            }

    return render(request, "attractions/search.html", context)

@login_required
def attraction_detail(request, uuid):
    attraction = get_object_or_404(Attraction, uuid=uuid)
    fill_attraction_details(attraction)
    outing_form = OutingForm()

    if request.method == 'POST': # prevents submitting when user accidentally clicks back
        if request.POST.get("favourites", "") == 'Save to Favourites':
            attraction.saved_by.add(request.user.profile)
            messages.success(request, 'Attraction added to favourites.')
        elif request.POST.get("favourites", "") == 'Remove from Favourites':
            attraction.saved_by.remove(request.user.profile)
            messages.success(request, 'Attraction removed from favourites.')
        else:
            outing_form = OutingForm(request.POST)
            if  outing_form.is_valid():
                outing =  outing_form.save(False)
                outing.attraction = attraction # outing is to visit this attraction
                outing.creator = request.user.profile # outing is created by this user
                outing.save()
                return redirect("movie_night_detail_ui", outing.pk)

    if request.user.profile in attraction.saved_by.all(): # save/remove favourites button
        button_value = "Remove from Favourites"
    else:
        button_value = "Save to Favourites"

    context = {"page_group": "search", "attraction": attraction, "button_value": button_value, "outing_form": outing_form}

    return render(request, "attractions/single_attraction.html", context)


@login_required
def saved_attractions(request):
    attractions = request.user.profile.saved_attractions.all()
    
    context = {"page_group": "saved", "attractions": attractions}

    return render(request, "attractions/saved.html", context)