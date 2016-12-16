# -*- coding: utf-8 -*-
import datetime

import django_excel as excel

from django.contrib import messages

from graphos.sources.simple import SimpleDataSource
from graphos.renderers.gchart import LineChart, ColumnChart

from hidromed.izarnet.models import Izarnet
from hidromed.medidores.models import Medidor
from hidromed.users.models import Poliza_Medidor_User

#Get medidores
def GetMedidor(request, usuario):
	usuario_medidores = Poliza_Medidor_User.objects.filter(
		usuario=usuario)
	if not usuario_medidores:
		messages.error(request,
			'Su usuario no tiene medidores o pólizas asociados')
	return usuario_medidores

#Generar grafico de lineas
def GetChartFree(data, poliza, unidad, tipo):
	data_source = SimpleDataSource(data=data)
	title = 'PÓLIZA: ' + str(poliza) + ' (' + str(unidad) + ')' 
	if tipo == 'liena':
		return LineChart(data_source, options={'title': title})
	elif tipo == 'barras':
		return ColumnChart(data_source, options={'title': title})

#Pool de datos para generar los graficos
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
				if data_m.fecha < f_next:
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

#Exportar pool de datos en excel
def DownloadExcel(request, medidor, desde, hasta, periodo_datos, tipo_de_grafico):
	medidor = Medidor.objects.get(serial=medidor)
	if tipo_de_grafico == 'volumen_litros':
		value_header = 'Volumen (Litros)'
	else:
		value_header = 'Consumo (Litros)'
	data = GetData(
		Izarnet.objects.filter(
			medidor=medidor,
			fecha__range=[
				datetime.datetime.strptime(str(desde) + ' 00:00:00', '%Y-%m-%d %H:%M:%S'),
				datetime.datetime.strptime(str(hasta) + ' 23:59:00', '%Y-%m-%d %H:%M:%S')
			]).order_by('fecha'),
		int(periodo_datos),
		tipo_de_grafico)
	data[0][1] = value_header
	return excel.make_response_from_array(
    	data,
    	"xlsx",
    	file_name="Medidor_"+str(medidor.serial)+".xlsx")
