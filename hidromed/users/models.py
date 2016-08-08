# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from django.contrib.auth.models import AbstractUser
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from hidromed.empresas.models import Empresa, Poliza
from hidromed.medidores.models import Medidor

PERFILES = (
    ('0', 'Gratuito'),
)

@python_2_unicode_compatible
class User(AbstractUser):

    # First Name and Last Name do not cover name patterns
    # around the globe.
    name = models.CharField(_('Name of User'), blank=True, max_length=255)
    empresa = models.ForeignKey(Empresa, null=True, blank=True)
    medidor = models.ForeignKey(Medidor, null=True, blank=True)
    poliza = models.ForeignKey(Poliza, null=True, blank=True)
    perfil = models.CharField(
		max_length=1, choices=PERFILES, default=0)

    def __str__(self):
        return self.username

    def get_absolute_url(self):
        return reverse('users:detail', kwargs={'username': self.username})
