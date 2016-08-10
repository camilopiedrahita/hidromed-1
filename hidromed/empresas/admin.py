# coding=utf8
from django.contrib import admin

from .models import *

@admin.register(Empresa)
class AdminEmpresa(admin.ModelAdmin):
	list_display = ('id', 'nombre', 'nit',)

@admin.register(Poliza)
class AdminPoliza(admin.ModelAdmin):
	list_display = ('id', 'numero', 'empresa',)