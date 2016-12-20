from __future__ import unicode_literals

from django.db import models
from django.utils.encoding import python_2_unicode_compatible

from hidromed.medidores.models import Medidor

#modelos correspondientes a la app de Izarnet
@python_2_unicode_compatible
class Izarnet(models.Model):
	medidor = models.ForeignKey(Medidor, default=None)
	fecha = models.DateTimeField()
	volumen = models.FloatField(default=None)
	consumo = models.FloatField(default=None)
	volumen_litros = models.FloatField(default=None)
	alarma = models.CharField(max_length=255)

	class Meta:
		verbose_name = 'Izarnet'
		verbose_name_plural = 'Izarnet'

	def __str__(self):
		return str(self.medidor)

@python_2_unicode_compatible
class IzarnetProcesados(models.Model):
	nombre = models.CharField(max_length=255)
	fecha = models.DateTimeField()
	estado = models.CharField(max_length=255)

	class Meta:
		verbose_name = 'Archivos Procesados'
		verbose_name_plural = 'Archivos Procesados'

	def __str__(self):
		return self.nombre