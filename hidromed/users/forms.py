# -*- coding: utf-8 -*-
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, HTML
from crispy_forms.bootstrap import FormActions


class CargueUsuarios(forms.Form):
	archivo_usuarios = forms.FileField()

	def __init__(self, *args, **kwargs):
		super(CargueUsuarios, self).__init__(*args, **kwargs)
		self.helper = FormHelper(self)
		self.helper.layout.append(
			FormActions(
				Submit('save', 'Crear'),
			)
		)