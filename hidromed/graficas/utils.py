# -*- coding: utf-8 -*-
import datetime
import numpy as np
import pandas as pd
import django_excel as excel

from django.contrib import messages

from graphos.sources.simple import SimpleDataSource
from graphos.renderers.gchart import AreaChart, ColumnChart
from dateutil.relativedelta import relativedelta

from hidromed.izarnet.models import Izarnet
from hidromed.medidores.models import Medidor
from hidromed.users.models import Poliza_Medidor_User

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
		data_medidor['anho'] == data_medidor['anho'].shift(-1), 0, 1)
	data_medidor['flag_mes'] = np.where(
		data_medidor['mes'] == data_medidor['mes'].shift(-1), 0, 1)
	data_medidor['flag_dia'] = np.where(
		data_medidor['dia'] == data_medidor['dia'].shift(-1), 0, 1)
	data_medidor['flag_hora'] = np.where(
		data_medidor['hora'] == data_medidor['hora'].shift(-1), 0, 1)
	data_medidor['flag_semana'] = np.where(
		data_medidor['semana'] == data_medidor['semana'].shift(-1), 0, 1)
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
		graph = AreaChart(
			data_source, height=500, width=1100, options={'title': title})
	elif tipo == 'barras':
		graph = ColumnChart(
			data_source, height=500, width=1100, options={'title': title})
	return graph

#Funcion sumatoria
def FuncSumatoria(data_medidor):

	#realizar sumatoria por periodo de datos
	data_medidor['reset'] = data_medidor['flag'].cumsum()
	data_medidor['consumo_acumulado'] = (
		data_medidor.groupby(['reset'])['consumo'].cumsum())
	data_medidor['consumo_acumulado'] = (
		data_medidor['consumo_acumulado'].shift(1))

	return data_medidor

#Funcion caudal promedio
def FuncCaudal(data_medidor):

	#calcular caudal promedio
	data_medidor['diferencia_minutos'] = (
		data_medidor['minutos'] - data_medidor['minutos'].shift(1))
	data_medidor['diferencia_minutos'] = np.where(
		data_medidor['diferencia_minutos'] == 0, 1, 
		data_medidor['diferencia_minutos'])
	data_medidor['caudal_promedio'] = (
		data_medidor['consumo'] / data_medidor['diferencia_minutos'] * 60)

	return data_medidor

#Pool de datos para generar los graficos
def GetData(data_medidor, periodo_datos, campo):

	#Convertir queryset en python pandas dataframe
	df = pd.DataFrame(list(data_medidor.values(
		'fecha', 'consumo', 'volumen_litros')))

	#obtener datos en periodo de datos
	new_data_medidor = GetPeriodoData(df, periodo_datos)

	#condicionale para los diferentes tipos de graficos
	if campo == 'consumo':

		#obtener consumo acumulado
		new_data_medidor = FuncSumatoria(new_data_medidor)
		campo = 'consumo_acumulado'
	
	elif campo == 'caudal':

		#obtener caudal promedio
		new_data_medidor = FuncCaudal(new_data_medidor)
		campo = 'caudal_promedio'

	#filtro campos del dataframe
	new_data_medidor = new_data_medidor[new_data_medidor['flag'] == 1]
	new_data_medidor = new_data_medidor[['fecha', campo]]

	#Agregar encabezado de columnas al dataframe 
	data = new_data_medidor.values.tolist()
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
			fecha__range=[desde, hasta]).order_by('fecha'),
		periodo_datos,
		tipo_de_grafico)
	data[0][1] = value_header
	return excel.make_response_from_array(
    	data,
    	"xlsx",
    	file_name="Medidor_"+str(medidor.serial)+".xlsx")

#fechas segun filtro rapido
def FiltroRapido(tipo_de_filtro, medidor):

	#declaracion de variables
	desde = '1986-02-12'
	hasta = '1986-02-12'
	
	if Izarnet.objects.filter(medidor=medidor):
		#obtener fecha del ultimo registro
		hasta = Izarnet.objects.filter(medidor=medidor).order_by('-fecha')[0].fecha

		#rango de timpo segun tipo de filtro
		if tipo_de_filtro == '1':
			desde = hasta - relativedelta(hours=1)
		elif tipo_de_filtro == '2':
			desde = hasta - relativedelta(days=1)
		elif tipo_de_filtro == '3':
			desde = hasta - relativedelta(weeks=1)
		elif tipo_de_filtro == '4':
			desde = hasta - relativedelta(months=1)
		elif tipo_de_filtro == '5':
			desde = hasta - relativedelta(months=2)
		elif tipo_de_filtro == '6':
			desde = hasta - relativedelta(years=1)

	return {'desde': desde, 'hasta': hasta}

