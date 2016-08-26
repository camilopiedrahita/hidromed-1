# -*- coding: utf-8 -*-
from django.shortcuts import render

from django.contrib import messages
from django.contrib.auth.decorators import login_required

from chartit import DataPool, Chart

from hidromed.izarnetv1.models import Izarnetv1
from hidromed.izarnetv2.models import Izarnetv2
from hidromed.medidores.models import Medidor
from hidromed.users.models import User, PolizaUser, MedidorUser

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
	usuario_medidores = MedidorUser.objects.filter(usuario=request.user)
	
	if not usuario_medidores:
		messages.error(request, 'Su usuario no tiene medidores asociados')
		data = ''
	else:
		grafico_izarnetv1 = []
		grafico_izarnetv2 = []
		for medidor in usuario_medidores:
			medidor = Medidor.objects.get(serial=medidor)
			if Izarnetv1.objects.filter(medidor=medidor).exists():
				grafico_izarnetv1.append(GetChartFree(
					medidor,
					Izarnetv1.objects.filter(medidor=medidor)))
			if Izarnetv2.objects.filter(medidor=medidor).exists():
				grafico_izarnetv2.append(GetChartFree(
					medidor,
					Izarnetv2.objects.filter(medidor=medidor)))
		
		charts_counter_izarnetv1 = GetCounter(grafico_izarnetv1, '1')
		charts_counter_izarnetv2 = GetCounter(grafico_izarnetv2, '2')

		data = {
			'grafico_izarnetv1': grafico_izarnetv1,
			'charts_counter_izarnetv1': charts_counter_izarnetv1,
			'grafico_izarnetv2': grafico_izarnetv2,
			'charts_counter_izarnetv2': charts_counter_izarnetv2,
		}

	return render(request, 'pages/grafico_gratis.html', {'data': data})