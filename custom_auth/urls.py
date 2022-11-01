from django.urls import include, path
from . import views

urlpatterns = [
    path('profile/', views.profile, name="profile"),    
    path('edit_profile/', views.edit_profile, name="edit_profile"),    
    path('profiles/', views.profiles, name='profiles'),
    path('profile/<str:pk>/', views.ProfileDetailView.as_view(), name='profile_detail'),
]
