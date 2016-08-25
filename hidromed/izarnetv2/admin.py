from django.contrib import admin

from .models import *

@admin.register(Izarnetv2)
class AdminIzarnetv2(admin.ModelAdmin):
	list_filter = ('medidor',)
	list_display = ('id', 'medidor', 'fecha', 'volumen_litros',
		'consumo', 'caudal', 'alarma',)

@admin.register(Izarnetv2Procesados)
class AdminIzarnetv2Procesados(admin.ModelAdmin):
	list_display = ('id', 'nombre', 'fecha', 'estado',)