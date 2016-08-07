from __future__ import unicode_literals

from django.db import models
from django.utils.encoding import python_2_unicode_compatible

from hidromed.empresas.models import Empresa

@python_2_unicode_compatible
class Medidor(models.Model):
	serial = models.CharField(max_length=255)
	empresa = models.ForeignKey(Empresa, default=None)

	def __str__(self):
		return self.serial
