# -*- coding: utf-8 -*-
from django import forms

import datetime

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

#Opciones para los select del formulario
TIPO_CHOICES = (
		('volumen_litros', 'Volumen Acumulado'),
		('consumo', 'Consumo Acumulado'),
		('caudal', 'Caudal Promedio'),
	)

PERIODO_CHOICES = (
		('60', 'Cada minuto'),
		('900', 'Cada 15 minutos'),
		('3600', 'Cada hora'),
		('86400', 'Cada día'),
		('604800', 'Cada semana'),
		('2592000', 'Cada mes'),
	)

GRAFICO_CHOICES = (
		('liena', 'Líena'),
		('barras', 'Barras'),
	)

#Formulario de filtros
class FiltrosForm(forms.Form):
	tipo_de_grafico = forms.ChoiceField(choices=TIPO_CHOICES)
	periodo_datos = forms.ChoiceField(choices=PERIODO_CHOICES)
	desde = forms.DateField(
		widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'date'}))
	hasta = forms.DateField(
		widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'date'}))
	grafico = forms.ChoiceField(choices=GRAFICO_CHOICES)
	helper = FormHelper()
	helper.add_input(Submit('filtro', 'Filtrar', css_class='btn-primary'))

	def __init__(self, *args, **kwargs):
		super(FiltrosForm, self).__init__(*args, **kwargs)