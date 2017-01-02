# -*- coding: utf-8 -*-
from django.shortcuts import render

from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .forms import *
from .models import *

def MedidoresView(request):
	
	#administracion de medidores padres, hijos
	error = False
	form = MedidoresForm()

	if request.method == 'POST':
		form = MedidoresForm(request.POST)

		if form.is_valid():
			#obtener datos del formulario
			medidor = form.cleaned_data['medidor']
			padre = form.cleaned_data['padre']
			hijos = form.cleaned_data['hijos']

			#asignar id de medidores padres
			if not padre == None:
				medidor.padreId = padre
				medidor.save()
			else:
				error = True

			for hijo in hijos:
				hijo.padreId = medidor
				hijo.save()

			#control de errores
			if error == True:
				messages.error(request, 
					'No seleccionó un medidor padre, por favor vuelva a intentarlo')
			else:
				messages.success(request, 'Los cambios se realizaron correctamente')

			#reiniciar formulario
			form = MedidoresForm()

		else:
			messages.error(request, 'No ha diligenciado todos los campos del formulario')

	data = { 'form': form, }

	return render(request, 'pages/medidores.html', {'data': data})

def LoadMedidorView(request):
	#vista ajax para modificar los select del formulario de medidores
	
	#variables
	medidores = []
	padre = ''

	#filtrar medidores dependiendo de las selecciones
	if 'medidor' in request.GET.keys() and 'padre' in request.GET.keys():
		medidor = request.GET['medidor']
		padre = request.GET['padre']
		medidores = Medidor.objects.exclude(id__in=[medidor, padre])
		
	elif 'medidor' in request.GET.keys():
		medidor = request.GET['medidor']
		medidores = Medidor.objects.exclude(id=medidor)

	data = { 
		'medidores': medidores,
		'padre': padre,
	}

	return render(request, 'ajax/fill_medidores.html', {'data': data})
