from django.contrib import admin

from .models import *

@admin.register(Medidor)
class AdminMedidor(admin.ModelAdmin):
	list_display = ('id', 'serial',)

@admin.register(Medidor_Cliente)
class AdminMedidor(admin.ModelAdmin):
	list_display = ('id', 'medidor', 'cliente',)

@admin.register(Medidor_Acueducto)
class AdminMedidor(admin.ModelAdmin):
	list_display = ('id', 'medidor', 'acueducto',)
