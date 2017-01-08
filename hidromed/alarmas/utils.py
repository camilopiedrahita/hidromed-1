# -*- coding: utf-8 -*-
import datetime

from dateutil.relativedelta import relativedelta

from hidromed.izarnet.models import Izarnet
from hidromed.medidores.models import Medidor
from hidromed.users.models import Poliza_Medidor_User

#generar alarmas mes actual
def AlarmasMesActual(usuario_medidores):

	#Perido de datos meses actual
	fecha_actual = datetime.datetime.now()

	#obtener datos de Izarnet
	if Izarnet.objects.filter(
		medidor__in=usuario_medidores.values('medidor'),
		fecha__year=fecha_actual.year,
		fecha__month=fecha_actual.month).exists():

		#datos de los medidores en el rango de fechas especificado
		datos_izarnet = Izarnet.objects.filter(
			medidor__in=usuario_medidores.values('medidor'),
			fecha__year=fecha_actual.year,
			fecha__month=fecha_actual.month)

		return datos_izarnet
