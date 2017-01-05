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
		title = ('Consumo acumulado mensual - ' + str(medidor))
		graph = AreaChart(
			data_source, height=500, width=1050, options={'title': title})

	#por cada medidor
	elif medidor == 'por cada medidor':
		title = ('Consumo acumulado total - ' + str(medidor))
		graph = ColumnChart(
			data_source, height=500, width=1050, options={'title': title})

	#grafico circular
	elif medidor == 'Porcentaje de cosumo':
		title = (str(medidor) + ' - por medidor')
		graph = PieChart(
			data_source, height=500, width=1050, options={'title': title})

	return graph

#get medidor y mes
def GetMedidoresLoc(data):

	#dividir tiempo en columnas
	data['mes'] = data['fecha'].dt.month
	data['dia'] = data['fecha'].dt.day

	#marcar localicacion de cada medidor en el dataframe
	data['flag_medidor'] = np.where(
		data['medidor'] == data['medidor'].shift(-1), 0, 1)
	data['flag_mes'] = np.where(
		data['mes'] == data['mes'].shift(-1), 0, 1)
	data['flag_dia'] = np.where(
		data['dia'] == data['dia'].shift(-1), 0, 1)

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

#get datos de interes
def GetInteresData(data):

	#consumo total
	consumo_total_seis_meses =  data['consumo'].sum()

	#consumo promedio mensual
	consumo_por_mes = data[data['flag'] == 1]
	promedio_consumo_mensual = consumo_por_mes['consumo_acumulado'].mean()
	if np.isnan(promedio_consumo_mensual): promedio_consumo_mensual = 0

	#obtener mes actual
	mes = str(datetime.datetime.now().month)

	#consumo mes actual
	consumo_por_mes['mes'] = consumo_por_mes['mes'].map(str)
	consumo_mes_actual = (
		consumo_por_mes[consumo_por_mes['mes'] == mes]['consumo_acumulado'].sum())

	#obtener consumo sumatoria por medidor
	data['flag'] = data['flag_dia']
	data = FuncSumatoria(data)

	#promedio consumo diario mes actual
	consumo_diario = data[data['flag'] == 1]
	consumo_diario['mes'] = consumo_diario['mes'].map(str)
	promedio_consumo_diario = (
		consumo_diario[consumo_diario['mes'] == mes]['consumo_acumulado'].mean())
	if np.isnan(promedio_consumo_diario): promedio_consumo_diario = 0

	#diccionario de datos
	data = {
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
	if Izarnet.objects.filter(medidor__in=medidores.values('medidor')).exists():

		#generar queryset
		data_izarnet = Izarnet.objects.filter(
			medidor__in=medidores.values('medidor'),
			fecha__range=[desde, hasta]
			).order_by('fecha').values('fecha', 'medidor', 'consumo', 'alarma')

		#convertir queryset en python pandas dataframe
		df = pd.DataFrame(list(data_izarnet))

		#marcar medidores
		df = GetMedidoresLoc(df)

		#obtener consumo sumatoria de todos los medidores
		df['flag'] = df['flag_mes']
		df = FuncSumatoria(df)

		#lista de datos sumatoria consumo todos medidores
		df_todos = df[df['flag'] == 1]
		df_todos = df_todos[['fecha', 'consumo_acumulado']]
		df_todos = df_todos.values.tolist()
		df_todos.insert(0,['Fecha', 'consumo_acumulado'])

		#obtener datos de interes
		datos_interes = GetInteresData(df)

		#obtener consumo sumatoria por medidor
		df['flag'] = df['flag_medidor']
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

		#diccionario de datos
		data = {
			'df_por_medidor': df_por_medidor,
			'datos_interes': datos_interes,
			'df_todos': df_todos,
		}

		return data

	
	