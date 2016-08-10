# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.shortcuts import render
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.views.generic import DetailView, ListView, RedirectView, UpdateView

from django.contrib.auth.mixins import LoginRequiredMixin

from .models import *
from .forms import CargueUsuarios
from hidromed.utils import CargueExcel
from hidromed.empresas.models import Empresa, Poliza
from hidromed.medidores.models import Medidor

def CrearUsuarios(request, data):
    for row in data.iterrows():
        nit = row[1]['ID NIT Empresa']
        nombre = row[1]['Empresa']
        poliza = row[1]['Póliza']
        serial = row[1]['Serial Medidor']
        username = row[1]['Nombre Usuario']
        if Empresa.objects.filter(nit=nit):
            empresa_id = Empresa.objects.get(nit=nit)
        else:
            empresa_id = Empresa.objects.create(
                nombre=nombre,
                nit=nit)
        if Poliza.objects.filter(numero=poliza):
            poliza_id = Poliza.objects.get(numero=poliza)
        else:
            poliza_id = Poliza.objects.create(
                numero=poliza,
                empresa=empresa_id)
        if Medidor.objects.filter(serial=serial):
            medidor_id = Medidor.objects.get(serial=serial)
        else:
            medidor_id = Medidor.objects.create(
                serial=serial,
                empresa=empresa_id)
        if User.objects.filter(username=username):
            user_id = User.objects.get(username=username)
        else:
            user_id = User.objects.create_user(
                username,
                '',
                'Hidromed')
            user_id.empresa = empresa_id
            user_id.perfil = 0
            user_id.save()
        if PolizaUser.objects.filter(poliza=poliza_id, usuario=user_id):
            pass
        else:
            PolizaUser.objects.create(
                poliza=poliza_id, 
                usuario=user_id)
        if MedidorUser.objects.filter(medidor=medidor_id, usuario=user_id):
            pass
        else:
            MedidorUser.objects.create(
                medidor=medidor_id, 
                usuario=user_id)

def CrearUsuariosView(request):
    if request.method == 'POST':
        form = CargueUsuarios(request.POST, request.FILES)
        if form.is_valid():
            data = CargueExcel(request.FILES['archivo_usuarios'])
            CrearUsuarios(request, data)
            messages.success(request, 'Usuarios creados correctamente')
    else:
        form = CargueUsuarios()
    return render(request, 'pages/crear_usuarios.html', {'form': form})

class UserDetailView(LoginRequiredMixin, DetailView):
    model = User
    # These next two lines tell the view to index lookups by username
    slug_field = 'username'
    slug_url_kwarg = 'username'


class UserRedirectView(LoginRequiredMixin, RedirectView):
    permanent = False

    def get_redirect_url(self):
        return reverse('users:detail',
                       kwargs={'username': self.request.user.username})


class UserUpdateView(LoginRequiredMixin, UpdateView):

    fields = ['name', ]

    # we already imported User in the view code above, remember?
    model = User

    # send the user back to their own page after a successful update
    def get_success_url(self):
        return reverse('users:detail',
                       kwargs={'username': self.request.user.username})

    def get_object(self):
        # Only get the User record for the user making the request
        return User.objects.get(username=self.request.user.username)


class UserListView(LoginRequiredMixin, ListView):
    model = User
    # These next two lines tell the view to index lookups by username
    slug_field = 'username'
    slug_url_kwarg = 'username'
