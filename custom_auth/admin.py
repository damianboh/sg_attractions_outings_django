from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Profile
from django.utils.translation import gettext_lazy as _

# custom user admin to include email fields instead of username fields
class CustomUserAdmin(UserAdmin): 
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (_("Personal info"), {"fields": ("name",)}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2"),
            },
        ),
    )
    list_display = ("email", "name", "is_staff")
    search_fields = ("email", "name") # changed first_name, last_name to name, changed username to email
    ordering = ("email",)

admin.site.register(User, CustomUserAdmin)
admin.site.register(Profile)