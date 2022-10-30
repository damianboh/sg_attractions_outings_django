from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import ProfileForm
from django.views import generic
from django.db.models import Q
from .models import Profile

@login_required
def profile(request):
    return render(request, "custom_auth/profile.html")


@login_required
def edit_profile(request):
    profile = request.user.profile
    form = ProfileForm(instance=profile)

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile')

    context = {'form': form}
    return render(request, 'custom_auth/edit_profile.html', context)


class ProfilesView(generic.ListView):
    login_required = True
    template_name = 'custom_auth/profiles.html'
    context_object_name = 'profiles'

    def get_queryset(self):
        return Profile.objects.order_by('name')


def searchProfiles(request):
    search_query = ''

    if request.GET.get('search_query'):
        search_query = request.GET.get('search_query')

    # Return profiles whose search query in request matches name, email, about
    profiles = Profile.objects.distinct().filter(
        Q(name__icontains=search_query) |
        Q(email__icontains=search_query) |
        Q(about__icontains=search_query)
    )

    return profiles, search_query