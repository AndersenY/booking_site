from django.contrib import admin

# Register your models here.

from .models import Apartment
from .models import Calendar


@admin.register(Calendar)
class CalendarAdmin(admin.ModelAdmin):
    list_display = ('id', 'booked_dates')


@admin.register(Apartment)
class ApartmentAdmin(admin.ModelAdmin):
    list_display = ('description', 'price_per_night', 'link', 'calendar')
