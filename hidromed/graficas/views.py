# -*- coding: utf-8 -*-
from django.shortcuts import render

from django.contrib import messages
from django.contrib.auth.decorators import login_required

from chartit import DataPool, Chart

from hidromed.izarnetv1.models import Izarnetv1
from hidromed.izarnetv2.models import Izarnetv2
from hidromed.medidores.models import Medidor
from hidromed.polizas.models import Poliza
from hidromed.users.models import User, Poliza_Medidor_User
from .forms import FiltrosForm

def GetChartFree(medidor, filtro):
	data = \
		DataPool (
			series = 
			[{
				'options': {'source': filtro},
				'terms': [
					'fecha',
					'consumo']}
			])

	cht = Chart(
			datasource = data,
			series_options =
				[{'options':{
					'type': 'line',
					'stacking': False},
				'terms':{
					'fecha': [
					'consumo']
				}}],
			chart_options =
				{'title': {
					'text': 'Medidor ' + medidor.serial},
				'xAxis': {
					'title': {
						'text': 'Datos'}}})
	return cht

@login_required
def FreeChart(request):
	usuario_medidores = Poliza_Medidor_User.objects.filter(usuario=request.user)
	
	if not usuario_medidores:
		messages.error(request, 'Su usuario no tiene medidores o pólizas asociados')
		data = ''
	else:
		form = FiltrosForm()
		medidores = []
		polizas = []
		tipo_de_grafico = ''
		periodo_datos = ''
		desde = ''
		hasta = ''
		medidor_request = ''
		for registro in usuario_medidores:
			medidor = Medidor.objects.get(serial=registro.medidor)
			poliza = Poliza.objects.get(numero=registro.poliza)
			medidores.append(medidor)
			polizas.append(poliza)

		if 'medidor' in request.GET.keys():
			medidor_request = request.GET.get('medidor')

		if request.method == 'POST':
			form = FiltrosForm(request.POST)
			if form.is_valid():
				tipo_de_grafico = form.cleaned_data['tipo_de_grafico']
				periodo_datos = form.cleaned_data['periodo_datos']
				desde = form.cleaned_data['desde']
				hasta = form.cleaned_data['hasta']

		print ('tipo_de_grafico')
		print (tipo_de_grafico)
		print ('periodo_datos')
		print (periodo_datos)
		print ('desde')
		print (desde)
		print ('hasta')
		print (hasta)
		print ('medidor_request')
		print (medidor_request)

		"""
		graficos = []
		for medidor in usuario_medidores:
			medidor = Medidor.objects.get(serial=medidor.medidor)
			if Izarnetv1.objects.filter(medidor=medidor).exists():
				graficos.append(GetChartFree(
					medidor,
					Izarnetv1.objects.filter(medidor=medidor)))
			if Izarnetv2.objects.filter(medidor=medidor).exists():
				graficos.append(GetChartFree(
					medidor,
					Izarnetv2.objects.filter(medidor=medidor)))
		
		#charts_counter = GetCounter(graficos, '1')
		"""
		data = {
			#'graficos': graficos,
			#'charts_counter': charts_counter,
			'medidores': medidores,
			'polizas': polizas,
			'form': form,
		}

	return render(request, 'pages/grafico_gratis.html', {'data': data})