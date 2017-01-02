# coding=utf8
from __future__ import unicode_literals

from django.db import models
from django.utils.encoding import python_2_unicode_compatible

from hidromed.empresas.models import Cliente, Acueducto

#modelos correspondientes a los medidores
@python_2_unicode_compatible
class Medidor(models.Model):
	serial = models.CharField(max_length=255)
	padreId = models.ForeignKey('self', default=None, null=True, blank=True)

	def __str__(self):
		return self.serial

@python_2_unicode_compatible
class Medidor_Cliente(models.Model):
	medidor = models.ForeignKey(Medidor, default=None, null=True, blank=True)
	cliente = models.ForeignKey(Cliente, default=None, null=True, blank=True)

	class Meta:
		verbose_name = 'Medidor vs Cliente'
		verbose_name_plural = 'Medidor vs Clientes'

	def __str__(self):
		relacion = (u'%s' % self.medidor + ' - '
			u'%s' % self.cliente )
		return relacion

@python_2_unicode_compatible
class Medidor_Acueducto(models.Model):
	medidor = models.ForeignKey(Medidor, default=None, null=True, blank=True)
	acueducto = models.ForeignKey(Acueducto, default=None, null=True, blank=True)

	class Meta:
		verbose_name = 'Medidor vs Acueducto'
		verbose_name_plural = 'Medidor vs Acueductos'

	def __str__(self):
		relacion = (u'%s' % self.medidor + ' - '
			u'%s' % self.acueducto )
		return relacion
