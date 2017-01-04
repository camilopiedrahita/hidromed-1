# -*- coding: utf-8 -*-
import datetime
import numpy as np
import pandas as pd

from graphos.sources.simple import SimpleDataSource
from graphos.renderers.gchart import AreaChart
from dateutil.relativedelta import relativedelta

from hidromed.izarnet.models import Izarnet
from hidromed.medidores.models import Medidor
from hidromed.users.models import Poliza_Medidor_User
from hidromed.graficas.utils import FuncSumatoria

#Generar grafico
def GetChart(data, medidor):

	#todos los medidores
	data_source = SimpleDataSource(data=data)
	title = ('Consumo acumulado - ' + str(medidor))
	graph = AreaChart(
		data_source, height=500, width=1050, options={'title': title})

	return graph

#get medidor y mes
def GetMedidoresLoc(data):

	#dividir tiempo en columnas
	data['mes'] = data['fecha'].dt.month

	#marcar localicacion de cada medidor en el dataframe
	data['flag_medidor'] = np.where(
		data['medidor'] == data['medidor'].shift(-1), 0, 1)
	data['flag'] = np.where(
		data['mes'] == data['mes'].shift(-1), 0, 1)

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

		#obtener consumo sumatoria de los medidores
		df = FuncSumatoria(df)

		#lista de datos sumatoria consumo todos medidores
		df_todos = df[df['flag'] == 1]
		df_todos = df_todos[['fecha', 'consumo_acumulado']]
		df_todos = df_todos.values.tolist()
		df_todos.insert(0,['Fecha', 'consumo_acumulado'])

		#lista de datos sumatoria consumo cada medidor
		df_por_medidor = []

		print (df)

		return {'df_todos': df_todos, 'df_por_medidor': df_por_medidor}

	
	