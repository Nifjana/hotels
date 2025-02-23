from django.contrib import admin
from myApp.models import Owner, CustomUser, Hotel, Room

admin.site.register(Owner)
admin.site.register(Room)
admin.site.register(Hotel)
admin.site.register(CustomUser) 
