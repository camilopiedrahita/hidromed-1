# -*- coding: utf-8 -*-
from django import forms

import datetime

#Opciones para los select del formulario
TIPO_CHOICES = (
		('volumen_litros', 'Volumen Acumulado'),
		('consumo', 'Consumo Acumulado'),
		('caudal', 'Caudal Promedio'),
	)

GRAFICO_CHOICES = (
		('liena', 'Línea'),
		('barras', 'Barras'),
	)

FILTRO_CHOICES = (
		('1', 'Última hora'),
		('2', 'Último día'),
		('3', 'Última semana'),
		('4', 'Último mes'),
		('5', 'Últimos tres meses'),
		('6', 'Último año'),
		('7', 'Personalizado'),
	)

PERIODO_CHOICES = (
		('1', 'Cada minuto'),
		('2', 'Cada 15 minutos'),
		('3', 'Cada hora'),
		('4', 'Cada día'),
		('5', 'Cada semana'),
		('6', 'Cada mes'),
	)

INPUT_DATE_FORMATS = (
	'%d/%m/%Y',
	'%m/%d/%Y',
	'%Y-%m-%d'
	)

#Formulario de filtros
class FiltrosForm(forms.Form):
	desde = forms.DateField(
		required=False,
		input_formats=INPUT_DATE_FORMATS,
		widget=forms.TextInput(attrs={
			'class': 'form-control', 
			'type': 'date',
			'placeholder': 'mm/dd/yyyy'}))
	hasta = forms.DateField(
		required=False,
		input_formats=INPUT_DATE_FORMATS,
		widget=forms.TextInput(attrs={
			'class': 'form-control', 
			'type': 'date',
			'placeholder': 'mm/dd/yyyy'}))
	tipo_de_grafico = forms.ChoiceField(choices=TIPO_CHOICES)
	grafico = forms.ChoiceField(choices=GRAFICO_CHOICES)
	tipo_de_filtro = forms.ChoiceField(choices=FILTRO_CHOICES)
	periodo_datos = forms.ChoiceField(choices=PERIODO_CHOICES)
