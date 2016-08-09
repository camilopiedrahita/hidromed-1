# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.shortcuts import render
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.views.generic import DetailView, ListView, RedirectView, UpdateView

from django.contrib.auth.mixins import LoginRequiredMixin

from .models import User
from .forms import CargueUsuarios
from hidromed.utils import CargueExcel

def CrearUsuarios(data):
    for row in data.iterrows():
        nit = row[1]['ID NIT Empresa']
        empresa = row[1]['Empresa']
        poliza = row[1]['Póliza']
        serial = row[1]['Serial Medidor']
        username = row[1]['Nombre Usuario']


def CrearUsuariosView(request):
    if request.method == 'POST':
        form = CargueUsuarios(request.POST, request.FILES)
        if form.is_valid():
            data = CargueExcel(request.FILES['archivo_usuarios'])
            CrearUsuarios(data)
            messages.success(request, 'Archivo cargado correctamente')
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
