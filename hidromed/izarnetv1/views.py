from django.shortcuts import render

from chartit import DataPool, Chart

from hidromed.izarnetv2.models import Izarnetv2

def FreeChartIzv1(request):
	data = \
		DataPool (
			series = 
			[{
				'options': {'source': Izarnetv2.objects.all()},
				'terms': [
					'medidor',
					'volumen_litros']}
			])

	cht = Chart(
			datasource = data,
			series_options =
				[{'options':{
					'type': 'line',
					'stacking': False},
				'terms':{
					'medidor': [
					'volumen_litros']
				}}],
			chart_options =
				{'title': {
					'text': 'Muestra'},
				'xAxis': {
					'title': {
						'text': 'Nada'}}})

	return render(request, 'pages/grafico_gratis.html', {'data': cht})