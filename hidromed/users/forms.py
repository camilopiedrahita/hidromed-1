# -*- coding: utf-8 -*-
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, HTML
from crispy_forms.bootstrap import FormActions


class CargueUsuarios(forms.Form):
	archivo_usuarios = forms.FileField()
	helper = FormHelper()
	helper.form_method = 'POST'
	helper.add_input(Submit('enviar', 'Crear', css_class='btn-primary'))