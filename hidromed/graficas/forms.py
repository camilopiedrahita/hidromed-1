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
		('1', 'Cada minuto'),
		('2', 'Cada 15 minutos'),
		('3', 'Cada hora'),
		('4', 'Cada día'),
		('5', 'Cada semana'),
		('6', 'Cada mes'),
	)

GRAFICO_CHOICES = (
		('liena', 'Líena'),
		('barras', 'Barras'),
	)

#Formulario de filtros
class FiltrosForm(forms.Form):
	desde = forms.DateField(
		widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'date'}))
	hasta = forms.DateField(
		widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'date'}))
	tipo_de_grafico = forms.ChoiceField(choices=TIPO_CHOICES)
	periodo_datos = forms.ChoiceField(choices=PERIODO_CHOICES)
	grafico = forms.ChoiceField(choices=GRAFICO_CHOICES)
	helper = FormHelper()
	helper.add_input(Submit('filtro', 'Filtrar', css_class='btn-primary'))

	def __init__(self, *args, **kwargs):
		super(FiltrosForm, self).__init__(*args, **kwargs)