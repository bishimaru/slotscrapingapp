from django.contrib import admin
from .models import *

# class TotalPayAdmin(admin.ModelAdmin):
#     list_display = ('store_name', 'date', 'totalpay')

admin.site.register(PachiSlotStore)
admin.site.register(BusinessDay)
admin.site.register(Slot)

