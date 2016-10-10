# coding=utf8
from django.contrib import admin
from django.contrib.admin import AdminSite

from .models import *

class AdminIzarnetv1Template(AdminSite):
	AdminSite.site_header = 'Hidromed S.A.'
	AdminSite.site_title = 'Hidromed S.A.'

@admin.register(Izarnet)
class AdminIzarnetv1(admin.ModelAdmin):

	def time(self, obj):
		return obj.fecha.strftime('%Y-%m-%d %H:%M:%S')

	time.short_description = 'Fecha'

	list_filter = ('medidor',)
	list_display = ('id', 'medidor', 'time', 'volumen', 'consumo',
		'volumen_litros', 'caudal', 'alarma',)

@admin.register(IzarnetProcesados)
class AdminIzarnetv1Procesados(admin.ModelAdmin):
	list_display = ('id', 'nombre', 'fecha', 'estado',)