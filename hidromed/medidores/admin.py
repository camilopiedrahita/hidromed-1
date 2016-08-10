from django.contrib import admin

from .models import *

@admin.register(Medidor)
class AdminMedidor(admin.ModelAdmin):
	list_display = ('id', 'serial', 'empresa',)
