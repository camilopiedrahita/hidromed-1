from __future__ import unicode_literals

from django.db import models
from django.utils.encoding import python_2_unicode_compatible

from hidromed.medidores.models import Medidor

@python_2_unicode_compatible
class Izarnetv1(models.Model):
	medidor = models.ForeignKey(Medidor, default=None)
	fecha = models.DateTimeField()
	volumen = models.FloatField(default=None)
	consumo = models.FloatField(default=None)
	volumen_litros = models.FloatField(default=None)
	caudal = models.FloatField(default=None)
	alarma = models.CharField(max_length=255)

	def __str__(self):
		return self.medidor