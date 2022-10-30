from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.views import generic
from django.db.models import Q
from .models import Profile
from .forms import SearchForm

@login_required
def index(request):
    return render(request, "attractions/index.html")

