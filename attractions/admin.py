from django.contrib import admin
from attractions.models.attractions import SearchTerm, Tag, Attraction
from attractions.models.outings import Outing, OutingInvitation, Comment

admin.site.register(SearchTerm)
admin.site.register(Tag)
admin.site.register(Attraction)
admin.site.register(Outing)
admin.site.register(OutingInvitation)
admin.site.register(Comment)