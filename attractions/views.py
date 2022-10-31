from datetime import timedelta
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect
from django.utils import timezone
from django.views import generic
from django.db.models import Q
from attractions.models.attractions import Attraction
from attractions.models.outings import Outing, OutingInvitation
from .forms import OutingForm, AttendanceForm, InviteeForm, CommentForm
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
        # save to or remove from favourites
        if request.POST.get("favourites", "") == 'Save to Favourites':
            attraction.saved_by.add(request.user.profile)
            messages.success(request, 'Attraction added to favourites.')
        elif request.POST.get("favourites", "") == 'Remove from Favourites':
            attraction.saved_by.remove(request.user.profile)
            messages.success(request, 'Attraction removed from favourites.')
        else:
            # creating outings
            outing_form = OutingForm(request.POST)
            if  outing_form.is_valid():
                outing =  outing_form.save(False)
                if (outing.start_time < timezone.now()):
                    outing_form.add_error("start_time", "Unable to create outing as start time is in the past.")
                    messages.error(request, 'Unable to create outing as start time is in the past.')
                else:
                    outing.attraction = attraction # outing is to visit this attraction
                    outing.creator = request.user.profile # outing is created by this user
                    outing.save()
                    return redirect("outing_detail", outing.pk)

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


@login_required
def outings(request):
    created_outings = request.user.profile.created_outings.all()
    invited_outings = Outing.objects.filter(
        outing_invites__in = OutingInvitation.objects.filter(invitee=request.user.profile),
    )

    context = {"page_group": "outings", "created_outings": created_outings, "invited_outings": invited_outings}
    
    return render(request, "attractions/outings.html", context)


@login_required
def outing_detail(request, pk):
    outing = get_object_or_404(Outing, pk=pk)  

    # by default no form rendered until below checks are passed
    invitee_form = None # only show to creator
    attendance_form = None # only show to invitee
    comment_form = CommentForm()

    # get all invitees for this outing
    invitees = {invitation.invitee for invitation in outing.outing_invites.all()}
    
    comments = outing.comments.all()

    is_creator = outing.creator == request.user.profile
    is_in_the_past = outing.start_time < timezone.now()

    if not is_creator:
        if request.user.profile not in invitees:
            # only creator or invitees can access
            raise PermissionDenied("You do not have access to this Outing.")

        invitation = outing.outing_invites.filter(invitee=request.user.profile).first()

        # only get request parameters for attendance if outing is in the future
        # only show attendance form if not creator, as creator is definitely attending
        if not is_in_the_past and request.method == "POST":
            attendance_form = AttendanceForm(request.POST, instance=invitation)
            if attendance_form.is_valid():
                attendance_form.save()
        else:
            attendance_form = AttendanceForm(instance=invitation)

    else:
        # only show invite form to creator to invite others
        if not is_in_the_past and request.method == "POST":
            invitee_form = InviteeForm(request.POST)

            if invitee_form.is_valid():
                invitee = invitee_form._userProfile
                
                # do not double create invitation
                if invitee == request.user.profile or invitee in invitees:
                    invitee_form.add_error(
                        "email", "That user is the creator or already invited."
                    )
                    messages.error(request, "That user is the creator or already invited.")
                else:
                    # creator invitation
                    OutingInvitation.objects.create(
                        invitee=invitee, outing=outing
                    )
                    return redirect(request.path)  # just reload the page
        else:
            invitee_form = InviteeForm()


    if request.method == "POST":
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():            
                comment =  comment_form.save(False)
                if comment.content != '':
                    comment.creator = request.user.profile
                    comment.outing = outing
                    comment.save()
                return redirect(request.path)

    context = {
                "page_group": "outings",
                "outing": outing,
                "is_creator": is_creator,
                "invitee_form": invitee_form,
                "attendance_form": attendance_form,
                "is_in_the_past": is_in_the_past,
                "comment_form": comment_form,
                "comments": comments,
                }

    return render(
        request, "attractions/single_outing.html", context)