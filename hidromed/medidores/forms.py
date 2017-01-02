# -*- coding: utf-8 -*-
from django import forms

from .models import *

#formulario administracion medidores
class MedidoresForm(forms.Form):
	medidor = forms.ModelChoiceField(queryset=Medidor.objects.all())
	padre = forms.ModelChoiceField(
		required=False,
		queryset=Medidor.objects.all())
	hijos = forms.ModelMultipleChoiceField(
		required=False,
		queryset=Medidor.objects.all())