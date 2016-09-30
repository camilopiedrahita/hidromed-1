# -*- coding: utf-8 -*-
from django.shortcuts import render

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from chartit import DataPool, Chart

from hidromed.izarnetv1.models import Izarnetv1
from hidromed.izarnetv2.models import Izarnetv2
from hidromed.medidores.models import Medidor
from hidromed.polizas.models import Poliza
from hidromed.users.models import User, Poliza_Medidor_User
from .forms import FiltrosForm

def GetChartFree(medidor, tipo_de_grafico, periodo_datos, 
	desde, hasta, filtro, izarnet):
	print ('periodo_datos')
	print (periodo_datos)

	data = \
		DataPool (
			series = 
			[{
				'options': {'source': filtro},
				'terms': [
					'fecha',
					tipo_de_grafico]}
			])

	cht = Chart(
			datasource = data,
			series_options =
				[{'options':{
					'type': 'line',
					'stacking': False},
				'terms':{
					'fecha': [
					tipo_de_grafico]
				}}],
			chart_options =
				{'title': {
					'text': 'Medidor ' + medidor.serial + ' - '+ izarnet},
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
		form = FiltrosForm()
		medidores = []
		polizas = []
		tipo_de_grafico = 'consumo'
		periodo_datos = ''
		desde = '1986-02-12'
		hasta = '1986-02-12'
		date_control = False
		for registro in usuario_medidores:
			medidor = Medidor.objects.get(serial=registro.medidor)
			poliza = Poliza.objects.get(numero=registro.poliza)
			medidores.append(medidor)
			polizas.append(poliza)

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

		graficos = []
		medidor = Medidor.objects.get(serial=medidor_request)
		if Izarnetv1.objects.filter(medidor=medidor).exists():
			if Izarnetv1.objects.filter(medidor=medidor, 
					fecha__range=[desde, hasta]):
				graficos.append(GetChartFree(
					medidor,
					tipo_de_grafico,
					periodo_datos,
					desde,
					hasta,
					Izarnetv1.objects.filter(medidor=medidor, 
						fecha__range=[desde, hasta]),
					'Izarnet 1'))
				date_control = False
			else:
				date_control = True

		if Izarnetv2.objects.filter(medidor=medidor).exists():
			if Izarnetv2.objects.filter(medidor=medidor,
					fecha__range=[desde, hasta]):
				graficos.append(GetChartFree(
					medidor,
					tipo_de_grafico,
					periodo_datos,
					desde,
					hasta,
					Izarnetv2.objects.filter(medidor=medidor,
						fecha__range=[desde, hasta]),
					'Izarnet 2'))
				date_control = False
			else:
				date_control = True
		
		if date_control == True:
			messages.warning(request, 'Por favor seleccione un rango de fechas')

		charts_counter = GetCounter(graficos, '1')
		data = {
			'graficos': graficos,
			'medidores': medidores,
			'polizas': polizas,
			'form': form,
			'charts_counter': charts_counter,
		}

	return render(request, 'pages/grafico_gratis.html', {'data': data})