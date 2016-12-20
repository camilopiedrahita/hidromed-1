# -*- coding: utf-8 -*-
import datetime
import numpy as np
import pandas as pd
import django_excel as excel

from django.contrib import messages

from graphos.sources.simple import SimpleDataSource
from graphos.renderers.gchart import LineChart, ColumnChart

from hidromed.izarnet.models import Izarnet
from hidromed.medidores.models import Medidor
from hidromed.users.models import Poliza_Medidor_User

#variables Globales
f_next = '1986-02-12'

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
		graph = LineChart(data_source, options={'title': title})
	elif tipo == 'barras':
		graph = ColumnChart(data_source, options={'title': title})
	return graph

#Funcion comparar fechas
def FucnFechas(row, periodo_datos):

	#Declaracion de variables
	global f_next

	#Comparar - obtener nueva fecha
	if row['fecha'] >= f_next:
		f_next = row['fecha'] + datetime.timedelta(0, int(periodo_datos))

	return f_next

#Pool de datos para generar los graficos
def GetData(data_medidor, periodo_datos, campo):

	#Declararcion de variables
	global f_next

	#Convertir queryset en python pandas dataframe
	df = pd.DataFrame(list(data_medidor.values('fecha', campo)))
	
	#obtener datos en periodo de datos
	f_next = df['fecha'][0] + datetime.timedelta(0, int(periodo_datos))
	df['fecha_flag'] = df.apply(FucnFechas, axis=1, args={periodo_datos})
	df['flag'] = np.where(df['fecha_flag'] != df['fecha_flag'].shift(1), 1, 0)
	df = df[df['flag'] == 1]
	df = df[['fecha', campo]]

	#Agregar encabezado de columnas al dataframe 
	data = df.values.tolist()
	data.insert(0,['Fecha', campo])

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
