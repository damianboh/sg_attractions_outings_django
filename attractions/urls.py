from django.urls import path, include
from . import views

urlpatterns = [
    path('search/', views.search_attractions, name='search_attractions'),
    path('details/<str:uuid>/', views.attraction_detail, name='attraction_detail'),
    path('outings/', views.outings, name='outings'),
    path('outings/details/<int:pk>', views.outing_detail, name='outing_detail'),
    path('saved/', views.saved_attractions, name='saved_attractions'),
]