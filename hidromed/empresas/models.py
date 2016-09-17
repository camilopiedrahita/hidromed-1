from __future__ import unicode_literals

from django.db import models
from django.utils.encoding import python_2_unicode_compatible

@python_2_unicode_compatible
class Acueducto(models.Model):
	nombre = models.CharField(max_length=255)
	nit = models.CharField(max_length=50)

	def __str__(self):
		return self.nombre

@python_2_unicode_compatible
class Cliente(models.Model):
	nombre = models.CharField(max_length=255)
	nit = models.CharField(max_length=50)
	direccion = models.CharField(max_length=255)

	def __str__(self):
		return self.nombre
