# coding=utf8
from django.contrib import admin

from .models import *

@admin.register(Acueducto)
class AdminAcueducto(admin.ModelAdmin):
	list_display = ('id', 'nombre', 'nit',)

@admin.register(Cliente)
class AdminCliente(admin.ModelAdmin):
	list_display = ('id', 'nombre', 'nit', 'direccion',)