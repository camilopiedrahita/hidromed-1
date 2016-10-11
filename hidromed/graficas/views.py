# -*- coding: utf-8 -*-
import datetime

import django_excel as excel

from django.shortcuts import render

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from graphos.sources.simple import SimpleDataSource
from graphos.renderers.gchart import LineChart

from hidromed.izarnet.models import Izarnet
from hidromed.medidores.models import Medidor, Medidor_Acueducto
from hidromed.users.models import User, Poliza_Medidor_User

from .forms import FiltrosForm

def GetChartFree(data):
	data_source = SimpleDataSource(data=data)
	return LineChart(data_source)

def GetData(data_medidor, periodo_datos, campo):
	data = [['Fecha', campo]]
	data.append([data_medidor[0].fecha, getattr(data_medidor[0], campo)])
	f_inicial = data_medidor[0].fecha
	f_next = f_inicial + datetime.timedelta(0, periodo_datos)
	if campo == 'consumo':
		sumatoria = 0
		first = True
		for data_m in data_medidor:
			if not first == True:
				if data_m.fecha <= f_next:
					sumatoria += getattr(data_m, campo)
				else:
					data.append([data_m.fecha, sumatoria])
					sumatoria = getattr(data_m, campo)
					f_next = (data_m.fecha + datetime.timedelta(0, periodo_datos))
			first = False
	else:
		for data_m in data_medidor:
			if data_m.fecha == f_next:
				data.append([data_m.fecha, getattr(data_m, campo)])
				f_next = (data_m.fecha + datetime.timedelta(0, periodo_datos))
			elif data_m.fecha > f_next:
				data.append([data_m.fecha, getattr(data_m, campo)])
				f_next = (data_m.fecha + datetime.timedelta(0, periodo_datos))
	return data

#corregir
def DownloadExcel(request, medidor, desde, hasta, periodo_datos):
	medidor = Medidor.objects.get(serial=medidor)
	data = GetData(
		Izarnet.objects.filter(medidor=medidor,
			fecha__range=[desde, hasta]).order_by('fecha'),
		int(periodo_datos),
		Izarnet.objects.all())
	column_names = (['fecha', 'volumen_litros',
		'caudal', 'consumo_acumulado', 'alarma'])
	return excel.make_response_from_query_sets(
    	data,
    	column_names,
    	"xlsx",
    	file_name="Datos.xlsx")

@login_required
def FreeChart(request):
	usuario = request.user
	usuario_medidores = Poliza_Medidor_User.objects.filter(
		usuario=usuario)
	client_data = usuario
	acueducto_data = ''
	medidor = '0'
	desde = '0'
	hasta = '0'
	periodo_datos = '0'
	
	if not usuario_medidores:
		messages.error(request,
			'Su usuario no tiene medidores o pólizas asociados')
		data = ''
	else:
		form = FiltrosForm()
		graficos = []
		medidores = []
		tipo_de_grafico = 'volumen_litros'
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
		acueducto_data = Medidor_Acueducto.objects.get(
			medidor=medidor).acueducto

		if Izarnet.objects.filter(medidor=medidor,
			fecha__range=[desde, hasta]):
			data_medidor_Izarnet = GetData(
				Izarnet.objects.filter(
					medidor=medidor,fecha__range=[desde, hasta]).order_by('fecha'),
				periodo_datos,
				tipo_de_grafico)

		if Izarnet.objects.filter(medidor=medidor).exists():
			if Izarnet.objects.filter(medidor=medidor, 
					fecha__range=[desde, hasta]):
				graficos = GetChartFree(data_medidor_Izarnet)
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
			'periodo_datos': periodo_datos,
		}

	return render(request, 'pages/grafico_gratis.html', {'data': data})