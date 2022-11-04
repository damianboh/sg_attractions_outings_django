"""URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from django_registration.backends.activation.views import RegistrationView
from django.conf import settings
from django.conf.urls.static import static
from custom_auth.forms import RegistrationForm
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('admin_manager/', admin.site.urls),
    path(
        "accounts/register/",
        RegistrationView.as_view(form_class=RegistrationForm),
        name="django_registration_register",
    ),
    path("accounts/", include("django_registration.backends.activation.urls")),
    path("accounts/", include("django.contrib.auth.urls")),
    path("accounts/", include("custom_auth.urls")),    
    path("attractions/", include("attractions.urls")),  
    path("api/v1/", include("sg_attractions_outings.api_urls")), # api urls in separate file in same folder
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
