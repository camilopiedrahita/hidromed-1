from django.contrib import admin

from .models import *

@admin.register(Poliza)
class AdminMedidor(admin.ModelAdmin):
	list_display = ('id', 'numero',)

@admin.register(Poliza_Cliente)
class AdminMedidor(admin.ModelAdmin):
	list_display = ('id', 'poliza', 'cliente',)
	list_filter = ('cliente',)

@admin.register(Poliza_Acueducto)
class AdminMedidor(admin.ModelAdmin):
	list_display = ('id', 'poliza', 'acueducto',)
	list_filter = ('acueducto',)


