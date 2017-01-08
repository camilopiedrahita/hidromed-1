# -*- coding: utf-8 -*-
from django.shortcuts import render

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required

from hidromed.izarnet.models import Izarnet
from hidromed.medidores.models import Medidor
from hidromed.users.models import User, Poliza_Medidor_User
from hidromed.graficas.utils import GetMedidor

from .utils import *

#Vista de alarmas ultimo mes
@login_required
def UltimoMesView(request):

	#declaracion de variables
	data = {}
	usuario = request.user
	usuario_medidores = GetMedidor(request, usuario)

	#construccion del la interfaz
	if usuario_medidores:

		#obtener alarmas asociadas al usuario mes actual
		alarmas_mes_actual = AlarmasMesActual(usuario_medidores)
		alarmas_mes_actual = Paginator(alarmas_mes_actual, 25)

		page = request.GET.get('page')

		try:
			data_paginada = alarmas_mes_actual.page(page)
		except PageNotAnInteger:
			data_paginada = alarmas_mes_actual.page(1)
		except EmptyPage:
			data_paginada = alarmas_mes_actual.page(alarmas_mes_actual.num_pages)

		#diccionario de datos
		data = {
			'data_paginada': data_paginada,
		}

	return render(request, 'pages/alarmas_ultimomes.html', {'data': data})
