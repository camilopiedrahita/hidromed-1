from django.contrib import admin

from .models import *

@admin.register(Izarnetv1)
class AdminIzarnetv1(admin.ModelAdmin):
	list_display = ('id', 'medidor', 'fecha', 'volumen',
		'consumo', 'volumen_litros', 'caudal', 'alarma',)
