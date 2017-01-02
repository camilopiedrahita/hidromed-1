# -*- coding: utf-8 -*-
from django.shortcuts import render

from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .forms import *
from .models import *

def MedidoresView(request):
	
	#administracion de medidores padres, hijos
	form = MedidoresForm()
	data = { 'form': form, }
	return render(request, 'pages/medidores.html', {'data': data})

def LoadMedidorView(request):
	#vista ajax para modificar los select del formulario de medidores
	medidores = []

	#filtrar medidores dependiendo de las selecciones
	if 'medidor' in request.GET.keys() and 'padre' in request.GET.keys():
		medidor = request.GET['medidor']
		padre = request.GET['padre']
		medidores = Medidor.objects.exclude(id__in=[medidor, padre])
		
	elif 'medidor' in request.GET.keys():
		medidor = request.GET['medidor']
		medidores = Medidor.objects.exclude(id=medidor)

	data = { 'medidores': medidores, }

	return render(request, 'ajax/fill_medidores.html', {'data': data})
