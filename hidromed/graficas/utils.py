# -*- coding: utf-8 -*-

import time

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
sumatoria = 0

#Get periodo de datos
def GetPeriodoData(data_medidor, periodo_datos):

	#dividir tiempo en columnas
	data_medidor['anho'] = data_medidor['fecha'].dt.year
	data_medidor['mes'] = data_medidor['fecha'].dt.month
	data_medidor['dia'] = data_medidor['fecha'].dt.day
	data_medidor['hora'] = data_medidor['fecha'].dt.hour
	data_medidor['minutos'] = data_medidor['fecha'].dt.minute
	data_medidor['semana'] = data_medidor['fecha'].dt.week

	#flags segun periodo de tiempo
	data_medidor['flag_anho'] = np.where(
		data_medidor['anho'] == data_medidor['anho'].shift(1), 0, 1)
	data_medidor['flag_mes'] = np.where(
		data_medidor['mes'] == data_medidor['mes'].shift(1), 0, 1)
	data_medidor['flag_dia'] = np.where(
		data_medidor['dia'] == data_medidor['dia'].shift(1), 0, 1)
	data_medidor['flag_hora'] = np.where(
		data_medidor['hora'] == data_medidor['hora'].shift(1), 0, 1)
	data_medidor['flag_semana'] = np.where(
		data_medidor['semana'] == data_medidor['semana'].shift(1), 0, 1)
	data_medidor['flag_minuto'] = 1
	data_medidor['mod_15'] = data_medidor['minutos'] % 15
	
	#nuevo data frame con mod 15 invertido
	df = data_medidor['mod_15'][::-1]

	#flag para perido de 15 minutos
	data_medidor['flag_15'] = np.where(
		data_medidor['flag_hora'] == 1, 1,
		np.where(df == 14, 1,
			np.where(df > df.shift(1), 1, 0)))

	#asignando periodo de datos al dataframe
	if periodo_datos == '1':
		data_medidor['flag'] = data_medidor['flag_minuto']
	elif periodo_datos == '2':
		data_medidor['flag'] = data_medidor['flag_15']
	elif periodo_datos == '3':
		data_medidor['flag'] = data_medidor['flag_hora']
	elif periodo_datos == '4':
		data_medidor['flag'] = data_medidor['flag_dia']
	elif periodo_datos == '5':
		data_medidor['flag'] = data_medidor['flag_semana']
	elif periodo_datos == '6':
		data_medidor['flag'] = data_medidor['flag_mes']

	return data_medidor

#Get medidores
def GetMedidor(request, usuario):
	usuario_medidores = Poliza_Medidor_User.objects.filter(
		usuario=usuario)
	if not usuario_medidores:
		messages.error(request,
			'Su usuario no tiene medidores o pólizas asociados')
	return usuario_medidores

#Generar grafico de lineas
def GetChartFree(data, poliza, medidor, unidad, tipo):
	data_source = SimpleDataSource(data=data)
	title = (
		'PÓLIZA: ' + str(poliza) + ' (' + str(unidad) + ')' + 
		' - MEDIDOR: ' + str(medidor) + ' (' + str(unidad) + ')')
	if tipo == 'liena':
		graph = LineChart(data_source, options={'title': title})
	elif tipo == 'barras':
		graph = ColumnChart(data_source, options={'title': title})
	return graph

#Funcion sumatoria
def FuncSumatoria(row):

	#Declaracion de variables
	global sumatoria

	#Realizar sumatoria
	if row['flag'] == 1:
		sumatoria = row['consumo']
	else:
		sumatoria = sumatoria + row['consumo']

	return sumatoria

#Funcion caudal promedio
def FuncCaudal(row):

	#Declararcion de variables
	global f_next

	#Caluclar caudal
	minutos = ((row['fecha'] - f_next).total_seconds()) / 60
	if minutos == 0: minutos = 1
	caudal = row['consumo'] / minutos * 60
	f_next = row['fecha']

	return caudal

#Pool de datos para generar los graficos
def GetData(data_medidor, periodo_datos, campo):

	start = time.time()

	#Declararcion de variables
	global sumatoria

	#Convertir queryset en python pandas dataframe
	df = pd.DataFrame(list(data_medidor.values('fecha', 'consumo', 'volumen_litros')))

	#obtener datos en periodo de datos
	new_data_medidor = GetPeriodoData(df, periodo_datos)

	#condicionale para los diferentes tipos de graficos
	if campo == 'consumo':
		
		#obtener consumo acumulado
		new_data_medidor['consumo_acumulado'] = (
			new_data_medidor.apply(FuncSumatoria, axis=1))
		new_data_medidor['consumo_acumulado'] = (
			new_data_medidor['consumo_acumulado'].shift(1))
		campo = 'consumo_acumulado'

		print (new_data_medidor)
	
	elif campo == 'caudal':

		#para eliminar
		global f_next

		#obtener caudal promedio
		f_next = new_data_medidor['fecha'][0]
		new_data_medidor['caudal_promedio'] = (
			new_data_medidor.apply(FuncCaudal, axis=1))
		campo = 'caudal_promedio'

	#filtro campos del dataframe
	new_data_medidor = new_data_medidor[new_data_medidor['flag'] == 1]
	new_data_medidor = new_data_medidor[['fecha', campo]]

	#Agregar encabezado de columnas al dataframe 
	data = new_data_medidor.values.tolist()
	data.insert(0,['Fecha', campo])

	print ('Funcion GetData:')
	end = time.time() - start
	print (end)

	return data

#Exportar pool de datos en excel
def DownloadExcel(request, medidor, desde, hasta, periodo_datos, tipo_de_grafico):
	medidor = Medidor.objects.get(serial=medidor)
	if tipo_de_grafico == 'volumen_litros':
		value_header = 'Volumen (Litros)'
	else:
		value_header = 'Consumo (Litros)'
	f_desde = (datetime.datetime.strptime(
		str(desde) + ' 00:00:00', '%Y-%m-%d %H:%M:%S'))
	f_hasta = (datetime.datetime.strptime(
		str(hasta) + ' 23:59:00', '%Y-%m-%d %H:%M:%S'))
	data = GetData(
		Izarnet.objects.filter(
			medidor=medidor,
			fecha__range=[f_desde, f_hasta]).order_by('fecha'),
		periodo_datos,
		tipo_de_grafico)
	data[0][1] = value_header
	return excel.make_response_from_array(
    	data,
    	"xlsx",
    	file_name="Medidor_"+str(medidor.serial)+".xlsx")
