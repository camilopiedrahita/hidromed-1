from django.shortcuts import render_to_response

from chartit import DataPool, Chart

from .models import Izarnetv1

def FreeChartIzv1(request):
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

	return render_to_response('pages/grafico_gratis.html', {'data': cht})