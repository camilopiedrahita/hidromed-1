# -*- coding: utf-8 -*-
from django.shortcuts import render

from django.contrib.auth.decorators import login_required

from hidromed.izarnet.models import Izarnet
from hidromed.medidores.models import Medidor
from hidromed.users.models import User, Poliza_Medidor_User
from hidromed.graficas.utils import GetMedidor

from .utils import *

#Vista de tablero rapido
@login_required
def TablerRapidoView(request):

	#declaracion de variables
	data = {}
	graficos = []
	data_interes = []
	data_cirular = []
	data_por_medidor = []
	data_todos_medidores = []
	usuario = request.user
	usuario_medidores = GetMedidor(request, usuario)

	#construccion del la interfaz
	if usuario_medidores:

		#obtener medidores padres
		padres = Medidor.objects.filter(padreId=None)
		medidores_filtered = usuario_medidores.filter(medidor__in=padres)

		#obtener medidor en request
		if 'medidor' in request.GET.keys():
			medidor = request.GET['medidor']
			medidor = Medidor.objects.get(serial=medidor)

			#filtrar hijos del medidor del request
			hijos = Medidor.objects.filter(padreId=medidor)
			medidores_filtered = usuario_medidores.filter(medidor__in=hijos)

		else:
			medidor = ''

		#obtener data medidores
		data_medidores = GetData(medidores_filtered)

		if data_medidores != None:

			#generar graficos
			data_cirular_seis_meses = GetChart(data_medidores['df_por_medidor'], 'Porcentaje de consumo')
			data_cirular_mes_actual = GetChart(data_medidores['df_mes_actual'], 'Porcentaje de consumo')
			data_todos_medidores = GetChart(data_medidores['df_todos'], 'todos los medidores')
			data_por_medidor = GetChart(data_medidores['df_por_medidor'], 'por cada medidor')

			#diccionario de graficos
			graficos = {
				'data_cirular_seis_meses': data_cirular_seis_meses,
				'data_cirular_mes_actual': data_cirular_mes_actual,
				'data_todos_medidores': data_todos_medidores,
				'data_por_medidor': data_por_medidor,
			}

			#datos de interes
			data_interes = data_medidores['datos_interes']

		#diccionario de datos
		data = {
			'medidores_filtered': medidores_filtered,
			'usuario_medidores': usuario_medidores,
			'data_interes': data_interes,
			'graficos': graficos,
			'medidor': medidor,
		}

	return render(request, 'pages/tablero.html', {'data': data})