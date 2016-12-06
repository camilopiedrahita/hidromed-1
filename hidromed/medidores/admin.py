from django.contrib import admin

from .models import *

#registro de modelos en el admin del sitio
@admin.register(Medidor)
class AdminMedidor(admin.ModelAdmin):
	list_display = ('id', 'serial',)

@admin.register(Medidor_Cliente)
class AdminMedidor(admin.ModelAdmin):
	list_display = ('id', 'medidor', 'cliente',)
	list_filter = ('cliente',)

@admin.register(Medidor_Acueducto)
class AdminMedidor(admin.ModelAdmin):
	list_display = ('id', 'medidor', 'acueducto',)
	list_filter = ('acueducto',)
