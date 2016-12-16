# -*- coding: utf-8 -*-
import datetime

from django.shortcuts import render

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from hidromed.izarnet.models import Izarnet
from hidromed.medidores.models import Medidor, Medidor_Acueducto
from hidromed.users.models import User, Poliza_Medidor_User

from .forms import FiltrosForm
from .utils import * 


#Vista de graficos
@login_required
def FreeChartView(request):
	usuario = request.user
	usuario_medidores = Poliza_Medidor_User.objects.filter(
		usuario=usuario)
	client_data = usuario
	acueducto_data = ''
	medidor = '0'
	desde = '0'
	hasta = '0'
	periodo_datos = '0'
	tipo_de_grafico = 'volumen_litros'
	
	if not usuario_medidores:
		messages.error(request,
			'Su usuario no tiene medidores o pólizas asociados')
		data = ''
	else:
		form = FiltrosForm()
		graficos = []
		medidores = []
		periodo_datos = '0'
		desde = '1986-02-12'
		hasta = '1986-02-12'
		date_control = False
		for registro in usuario_medidores:
			medidor = Medidor.objects.get(serial=registro.medidor)
			medidores.append(medidor)

		medidor_request = medidores[0]

		if 'medidor' in request.GET.keys():
			medidor_request = request.GET.get('medidor')

		if request.method == 'POST':
			form = FiltrosForm(request.POST)
			if form.is_valid():
				tipo_de_grafico = form.cleaned_data['tipo_de_grafico']
				periodo_datos = form.cleaned_data['periodo_datos']
				desde = form.cleaned_data['desde']
				hasta = form.cleaned_data['hasta']
				grafico = form.cleaned_data['grafico']

		if periodo_datos == '1':
			periodo_datos = 60
		elif periodo_datos == '2':
			periodo_datos = 900
		elif periodo_datos == '3':
			periodo_datos = 3600
		elif periodo_datos == '4':
			periodo_datos = 86400

		medidor = Medidor.objects.get(serial=medidor_request)
		poliza = Poliza_Medidor_User.objects.get(
			medidor=medidor, usuario=request.user).poliza
		if Medidor_Acueducto.objects.filter(medidor=medidor):
			acueducto_data = Medidor_Acueducto.objects.get(
				medidor=medidor).acueducto

		if Izarnet.objects.filter(medidor=medidor,
			fecha__range=[desde, hasta]):
			data_medidor_Izarnet = GetData(
				Izarnet.objects.filter(
					medidor=medidor,
					fecha__range=[
						datetime.datetime.strptime(str(desde) + ' 00:00:00', '%Y-%m-%d %H:%M:%S'),
						datetime.datetime.strptime(str(hasta) + ' 23:59:00', '%Y-%m-%d %H:%M:%S')
					]).order_by('fecha'),
				periodo_datos,
				tipo_de_grafico)

		if Izarnet.objects.filter(medidor=medidor).exists():
			if Izarnet.objects.filter(medidor=medidor, 
					fecha__range=[desde, hasta]):
				graficos = GetChartFree(
					data_medidor_Izarnet,
					Poliza_Medidor_User.objects.get(medidor=medidor,
						usuario=usuario).poliza,
					'Litros',
					grafico)
				date_control = False
			else:
				date_control = True

		if date_control == True:
			messages.warning(request,
				'Por favor seleccione un rango de fechas')

		data = {
			'graficos': graficos,
			'medidores': medidores,
			'form': form,
			'client_data': client_data,
			'acueducto_data': acueducto_data,
			'medidor': str(medidor),
			'desde': desde,
			'hasta': hasta,
			'tipo_de_grafico': tipo_de_grafico,
			'periodo_datos': periodo_datos,
		}

	return render(request, 'pages/grafico_gratis.html', {'data': data})