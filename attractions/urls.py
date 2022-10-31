from django.urls import path, include
from . import views

urlpatterns = [
    path('search/', views.search_attractions, name='search_attractions'),
    path('<str:uuid>/', views.attraction_detail, name='attraction_detail'),
]