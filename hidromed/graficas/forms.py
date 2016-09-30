# -*- coding: utf-8 -*-
from django import forms

import datetime

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

TIPO_CHOICES = (
		('volumen_litros', 'Volumen Acumulado'),
		('consumo', 'Consumo'),
	)

PERIODO_CHOICES = (
		('1', 'Cada minuto'),
		('2', 'Cada 15 minutos'),
		('3', 'Cada hora'),
		('4', 'Cada día'),
	)

class FiltrosForm(forms.Form):
	tipo_de_grafico = forms.ChoiceField(choices=TIPO_CHOICES)
	periodo_datos = forms.ChoiceField(choices=PERIODO_CHOICES)
	desde = forms.DateField(
		widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'date'}))
	hasta = forms.DateField(
		widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'date'}))
	helper = FormHelper()
	helper.add_input(Submit('filtro', 'Filtrar', css_class='btn-primary'))

	def __init__(self, *args, **kwargs):
		super(FiltrosForm, self).__init__(*args, **kwargs)