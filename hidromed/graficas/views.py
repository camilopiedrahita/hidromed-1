# -*- coding: utf-8 -*-
import datetime

from django.shortcuts import render

from django.contrib import messages
from django.contrib.auth.decorators import login_required

from hidromed.izarnet.models import Izarnet
from hidromed.medidores.models import Medidor, Medidor_Acueducto, Medidor_Cliente
from hidromed.users.models import User, Poliza_Medidor_User

from .forms import FiltrosForm
from .utils import * 


#Vista de graficos
@login_required
def FreeChartView(request):

	#Inicializacion de variables
	unidad = 'Litros'
	usuario = request.user
	usuario_medidores = GetMedidor(request, usuario)
	acueducto_data = ''
	medidor = '0'
	desde = '1986-02-12'
	hasta = '1986-02-12'
	periodo_datos = '0'
	tipo_de_filtro = '7'
	tipo_de_grafico = 'volumen_litros'
	date_control = False
	form = FiltrosForm()
	graficos = []
	medidores = []
	data = {}

	#construccion del la interfaz
	if usuario_medidores:

		#Generar datos de medidores, y polizas
		for registro in usuario_medidores:
			medidores.append(Medidor.objects.get(serial=registro.medidor))

		if 'medidor' in request.GET.keys():
			medidor = Medidor.objects.get(serial=request.GET.get('medidor'))
		else:
			medidor = Medidor.objects.get(serial=medidores[0])

		poliza = Poliza_Medidor_User.objects.get(
			medidor=medidor, usuario=usuario).poliza

		#Datos del formulario
		if request.method == 'POST':
			form = FiltrosForm(request.POST)

			if form.is_valid():
				tipo_de_grafico = form.cleaned_data['tipo_de_grafico']
				periodo_datos = form.cleaned_data['periodo_datos']
				desde = form.cleaned_data['desde']
				hasta = form.cleaned_data['hasta']
				grafico = form.cleaned_data['grafico']
				tipo_de_filtro = form.cleaned_data['tipo_de_filtro']

				#filtro rapido
				if tipo_de_filtro != '7':
					rango = FiltroRapido(tipo_de_filtro, medidor)
					desde = rango['desde']
					hasta = rango['hasta']

				#unidades
				if tipo_de_grafico == 'caudal':
					unidad = 'm³ / Hora'
				elif tipo_de_grafico == 'consumo':
					unidad = 'm³'

			else:
				messages.error(request,
			'No ha diligenciado todos los campos del formulario')

		#formato fecha
		if tipo_de_filtro == '7' and not desde == None and not hasta == None:
			desde = (datetime.datetime.strptime(
				str(desde) + ' 00:00:00', '%Y-%m-%d %H:%M:%S'))
			hasta = (datetime.datetime.strptime(
				str(hasta) + ' 23:59:00', '%Y-%m-%d %H:%M:%S'))

		#datos del acueducto
		if Medidor_Acueducto.objects.filter(medidor=medidor):
			acueducto_data = Medidor_Acueducto.objects.get(
				medidor=medidor).acueducto

		#datos de la empresa cliente del medidor
		if Medidor_Cliente.objects.filter(medidor=medidor):
			client_data = Medidor_Cliente.objects.get(
				medidor=medidor).cliente

		#datos del medidor en Izarnet
		if Izarnet.objects.filter(medidor=medidor,
			fecha__range=[desde, hasta]):
			data_medidor_Izarnet = GetData(
				Izarnet.objects.filter(
					medidor=medidor,
					fecha__range=[desde, hasta]).order_by('fecha'),
				periodo_datos,
				tipo_de_grafico)

		#generar graficos
		if Izarnet.objects.filter(medidor=medidor).exists():
			if Izarnet.objects.filter(medidor=medidor, 
					fecha__range=[desde, hasta]):
				graficos = GetChartFree(
					data_medidor_Izarnet,
					Poliza_Medidor_User.objects.get(medidor=medidor,
						usuario=usuario).poliza,
					Poliza_Medidor_User.objects.get(medidor=medidor,
						usuario=usuario).medidor,
					unidad,
					grafico)
				date_control = False
			else:
				date_control = True

		#control de fechas
		if date_control == True:
			messages.warning(request,
				'Por favor seleccione un rango de fechas')

		#diccionario de datos
		data = {
			'graficos': graficos,
			'medidores': medidores,
			'form': form,
			'usuario': usuario,
			'client_data': client_data,
			'acueducto_data': acueducto_data,
			'medidor': str(medidor),
			'desde': desde,
			'hasta': hasta,
			'tipo_de_grafico': tipo_de_grafico,
			'periodo_datos': periodo_datos,
		}

	return render(request, 'pages/grafico_gratis.html', {'data': data})
