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

def GetCounter(graficos, version):
	string = ''
	counter = 0
	for chart in graficos:
		counter += 1
		string = (string + 'chart' + version + 
			'_' + str(counter) + ',')
	return string

@login_required
def FreeChart(request):
	usuario_medidores = Poliza_Medidor_User.objects.filter(usuario=request.user)
	
	if not usuario_medidores:
		messages.error(request, 'Su usuario no tiene medidores o pólizas asociados')
		data = ''
	else:
		medidores = []
		polizas = []
		for registro in usuario_medidores:
			medidor = Medidor.objects.get(serial=registro.medidor)
			poliza = Poliza.objects.get(numero=registro.poliza)
			medidores.append(medidor)
			polizas.append(poliza)
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
		}

	return render(request, 'pages/grafico_gratis.html', {'data': data})