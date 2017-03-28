# -*- coding: utf-8 -*-
import datetime
import numpy as np
import pandas as pd

from graphos.sources.simple import SimpleDataSource
from graphos.renderers.gchart import AreaChart, ColumnChart, PieChart
from dateutil.relativedelta import relativedelta

from hidromed.izarnet.models import Izarnet
from hidromed.medidores.models import Medidor
from hidromed.users.models import Poliza_Medidor_User
from hidromed.graficas.utils import FuncSumatoria

#Generar grafico
def GetChart(data, medidor):

	#definir data source y titulo
	data_source = SimpleDataSource(data=data)

	#todos los medidores
	if medidor == 'todos los medidores':
		title = ('Consumo acumulado mensual - ' + str(medidor) + 
			' - Unidad: m³')
		graph = ColumnChart(
			data_source, height=350, width='100%', options={'title': title})

	#por cada medidor
	elif medidor == 'por cada medidor':
		title = ('Consumo acumulado total - ' + str(medidor) + 
			' - Unidad: m³')
		graph = ColumnChart(
			data_source, height=350, width='100%', options={'title': title})

	#grafico circular
	elif medidor == 'Porcentaje de consumo':
		title = (str(medidor) + ' - por medidor' + 
			' - Unidad: m³')
		graph = PieChart(
			data_source, height=350, width='100%', options={'title': title})

	return graph

#get medidor y mes
def GetMedidoresLoc(data):

	#Conversion consumo de litros a metros cubicos
	data['consumo'] = data['consumo'] / 1000

	#dividir tiempo en columnas
	data['mes'] = data['fecha'].dt.month
	data['dia'] = data['fecha'].dt.day
	data['anho'] = data['fecha'].dt.year

	#marcar localicacion de cada medidor en el dataframe
	data['flag_medidor'] = np.where(
		data['medidor'] == data['medidor'].shift(-1), 0, 1)
	data['flag_mes'] = np.where(
		data['mes'] == data['mes'].shift(-1), 0, 1)
	data['flag_dia'] = np.where(
		data['dia'] == data['dia'].shift(-1), 0, 1)

	#marcar localicacion de cada medidor para sumatoria de consumo
	data['flag_medidor_consumo'] = np.where(
		data['medidor'] == data['medidor'].shift(1), 0, 1)
	data['flag_mes_consumo'] = np.where(
		data['mes'] == data['mes'].shift(1), 0, 1)
	data['flag_dia_consumo'] = np.where(
		data['dia'] == data['dia'].shift(1), 0, 1)

	return data

#get serial medidores
def GetMedidorname(data):

	#declaracion de variables
	id_medidores = []
	serial_medidores = []

	#get id y serial medidor
	for medidor in data:
		id_medidores.append(str(medidor.medidor.id))
		serial_medidores.append(str(medidor.medidor.serial))

	#diccionario de datos
	data = {
		'id_medidores': id_medidores, 
		'serial_medidores': serial_medidores
	}

	return data

#get data mes actual
def GetMesActual(data):

	#declaracion de variables
	mes = str(datetime.datetime.now().month)
	anho = str(datetime.datetime.now().year)

	#filtrar mes actual
	data['mes'] = data['mes'].map(str)
	data['anho'] = data['anho'].map(str)
	data = (data[((data['mes'] == mes) & (data['anho'] == anho))])

	#obtener sumatoria consumo para datos de interes
	data['flag'] = data['flag_mes']
	data['flag_consumo'] = data['flag_mes_consumo']
	data = FuncSumatoria(data)

	return data

#get datos de interes
def GetInteresData(data):

	#consumo total
	consumo_total_seis_meses =  data['consumo'].sum()

	#total de meses
	fecha_minima = data['fecha'].min().to_pydatetime()
	fecha_maxima = data['fecha'].max().to_pydatetime()
	total_meses = relativedelta(fecha_maxima, fecha_minima).months
	if total_meses == 0: total_meses = 1

	#consumo promedio mensual
	cant_meses = data['mes'].value_counts().count()
	promedio_consumo_mensual = consumo_total_seis_meses / cant_meses

	#consumo mes actual
	mes_actual = GetMesActual(data)
	consumo_mes_actual = mes_actual['consumo'].sum()

	#obtener consumo mes actual sumatoria por medidor
	cant_dias = mes_actual['dia'].value_counts().count()
	promedio_consumo_diario = consumo_mes_actual / cant_dias

	#alarmas mes actual
	mes_actual['alarmas_flag'] = np.where(
		((mes_actual['alarma'] != '0') | 
			(mes_actual['alarma'] != '') | 
			(mes_actual['alarma'].isnull())),
		1, 0)
	cant_alarmas = mes_actual['alarmas_flag'].sum()

	#diccionario de datos
	data = {
		'total_meses': total_meses,
		'cant_alarmas': cant_alarmas,
		'consumo_mes_actual': consumo_mes_actual,
		'promedio_consumo_diario': promedio_consumo_diario,
		'consumo_total_seis_meses': consumo_total_seis_meses,
		'promedio_consumo_mensual': promedio_consumo_mensual,
	}

	return data

#obtenere datos de izarnet
def GetData(medidores):

	#declaracion de variables
	data_izarnet = []

	#Perido de datos 6 meses
	hasta = datetime.datetime.now()
	desde = hasta - relativedelta(months=6)

	#obtener datos de Izarnet
	if Izarnet.objects.filter(
			medidor__in=medidores.values('medidor'),
			fecha__range=[desde, hasta]
		).exists():

		#generar queryset
		data_izarnet = Izarnet.objects.filter(
			medidor__in=medidores.values('medidor'),
			fecha__range=[desde, hasta]
			).order_by('medidor', 'fecha').values(
				'fecha', 'medidor', 'consumo', 'alarma')

		#convertir queryset en python pandas dataframe
		df = pd.DataFrame(list(data_izarnet))

		#marcar medidores
		df = GetMedidoresLoc(df)
		df_sum_total = GetMedidoresLoc(df.sort_values('fecha'))

		#obtener consumo sumatoria de todos los medidores
		df_sum_total['flag'] = df_sum_total['flag_mes']
		df_sum_total['flag_consumo'] = df_sum_total['flag_mes_consumo']
		df_sum_total = FuncSumatoria(df_sum_total)

		#lista de datos sumatoria consumo todos medidores
		df_todos = df_sum_total[df_sum_total['flag'] == 1]
		df_todos = df_todos[['fecha', 'consumo_acumulado']]
		df_todos = df_todos.values.tolist()
		df_todos.insert(0,['Fecha', 'consumo_acumulado'])

		#obtener sumatoria consumo para datos de interes
		df['flag'] = df['flag_mes']
		df['flag_consumo'] = df['flag_mes_consumo']
		df = FuncSumatoria(df)

		#obtener datos de interes
		datos_interes = GetInteresData(df)

		#obtener consumo sumatoria por medidor
		df['flag'] = df['flag_medidor']
		df['flag_consumo'] = df['flag_medidor_consumo']
		df = FuncSumatoria(df)

		#serial de los medidores
		medidores_serial = GetMedidorname(medidores)

		#reemplazar id medidor por serial medidor
		df['medidor'] = df['medidor'].map(str).replace(
			medidores_serial['id_medidores'],
			medidores_serial['serial_medidores'])

		#lista de datos sumatoria consumo cada medidor
		df_por_medidor = df[df['flag'] == 1]
		df_por_medidor = df_por_medidor[['medidor', 'consumo_acumulado']]
		df_por_medidor = df_por_medidor.values.tolist()
		df_por_medidor.insert(0,['Medidor', 'consumo_acumulado'])

		#obtener mes actual
		df_mes_actual = GetMesActual(df)

		#lista de datos mes actual
		df_mes_actual = df_mes_actual[df_mes_actual['flag'] == 1]
		df_mes_actual = df_mes_actual[['medidor', 'consumo_acumulado']]
		df_mes_actual = df_mes_actual.values.tolist()
		df_mes_actual.insert(0,['Medidor', 'consumo_acumulado'])

		#diccionario de datos
		data = {
			'df_por_medidor': df_por_medidor,
			'df_mes_actual': df_mes_actual,
			'datos_interes': datos_interes,
			'df_todos': df_todos,
		}

		return data

