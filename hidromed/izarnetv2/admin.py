from django.contrib import admin

from .models import *

@admin.register(Izarnetv2)
class AdminIzarnetv2(admin.ModelAdmin):
	list_display = ('id', 'medidor', 'fecha', 'volumen_litros',
		'consumo', 'caudal', 'alarma',)
