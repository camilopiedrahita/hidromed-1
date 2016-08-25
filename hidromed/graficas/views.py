from django.shortcuts import render

from chartit import DataPool, Chart

from hidromed.izarnetv1.models import Izarnetv1
from hidromed.izarnetv2.models import Izarnetv2
from hidromed.users.models import User, PolizaUser, MedidorUser

def FreeChart(request):
	data = \
		DataPool (
			series = 
			[{
				'options': {'source': Izarnetv1.objects.all()},
				'terms': [
					'volumen',
					'volumen_litros']}
			])

	cht = Chart(
			datasource = data,
			series_options =
				[{'options':{
					'type': 'line',
					'stacking': False},
				'terms':{
					'volumen': [
					'volumen_litros']
				}}],
			chart_options =
				{'title': {
					'text': 'Muestra'},
				'xAxis': {
					'title': {
						'text': 'Nada'}}})

	return render(request, 'pages/grafico_gratis.html', {'data': cht})