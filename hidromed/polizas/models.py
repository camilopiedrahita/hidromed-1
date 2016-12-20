# coding=utf8
from __future__ import unicode_literals

from django.db import models
from django.utils.encoding import python_2_unicode_compatible

from hidromed.empresas.models import Cliente, Acueducto

#modelos correspondientes a las polizas
@python_2_unicode_compatible
class Poliza(models.Model):
	numero = models.CharField(max_length=255)

	def __str__(self):
		return self.numero

@python_2_unicode_compatible
class Poliza_Cliente(models.Model):
	poliza = models.ForeignKey(Poliza, default=None, null=True, blank=True)
	cliente = models.ForeignKey(Cliente, default=None, null=True, blank=True)

	class Meta:
		verbose_name = 'Póliza vs Cliente'
		verbose_name_plural = 'Pólizas vs Clientes'

	def __str__(self):
		relacion = (u'%s' % self.poliza + ' - '
			u'%s' % self.cliente )
		return relacion

@python_2_unicode_compatible
class Poliza_Acueducto(models.Model):
	poliza = models.ForeignKey(Poliza, default=None, null=True, blank=True)
	acueducto = models.ForeignKey(Acueducto, default=None, null=True, blank=True)

	class Meta:
		verbose_name = 'Póliza vs Acueducto'
		verbose_name_plural = 'Pólizas vs Acueductos'

	def __str__(self):
		relacion = (u'%s' % self.poliza + ' - '
			u'%s' % self.acueducto )
		return relacion
