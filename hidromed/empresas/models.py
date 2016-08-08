from __future__ import unicode_literals

from django.db import models
from django.utils.encoding import python_2_unicode_compatible

@python_2_unicode_compatible
class Empresa(models.Model):
	nombre = models.CharField(max_length=255)
	nit = models.CharField(max_length=50)

	def __str__(self):
		return self.nombre

@python_2_unicode_compatible
class Poliza(models.Model):
	numero = models.CharField(max_length=255)
	empresa = models.ForeignKey(Empresa, default=None)

	def __str__(self):
		return self.numero