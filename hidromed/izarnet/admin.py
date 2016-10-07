# coding=utf8
from django.contrib import admin
from django.contrib.admin import AdminSite

from .models import *

class AdminIzarnetv1Template(AdminSite):
	AdminSite.site_header = 'Hidromed S.A.'
	AdminSite.site_title = 'Hidromed S.A.'

@admin.register(Izarnet)
class AdminIzarnetv1(admin.ModelAdmin):
	list_filter = ('medidor',)
	list_display = ('id', 'medidor', 'fecha', 'volumen', 'consumo',
		'consumo_acumulado', 'volumen_litros', 'caudal', 'alarma',)

@admin.register(IzarnetProcesados)
class AdminIzarnetv1Procesados(admin.ModelAdmin):
	list_display = ('id', 'nombre', 'fecha', 'estado',)