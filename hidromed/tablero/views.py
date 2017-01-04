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
def TablerRapido(request):

	#declaracion de variables
	data = {}
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

		#generar graficos
		data_todos_medidores = GetChart(data_medidores['df_todos'], 'todos los medidores')

		#diccionario de datos
		data = {
			'data_todos_medidores': data_todos_medidores,
			'medidores_filtered': medidores_filtered,
			'usuario_medidores': usuario_medidores,
			'medidor': medidor,
		}

	return render(request, 'pages/tablero.html', {'data': data})