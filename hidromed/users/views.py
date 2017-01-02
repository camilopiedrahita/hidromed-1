# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.views.generic import DetailView, ListView, RedirectView, UpdateView

from django.contrib.auth.mixins import LoginRequiredMixin

from .models import *
from .forms import CargueUsuarios
from .utils import CrearUsuarios

from hidromed.utils import CargueExcel

#Vista de cargue de usuarios
@login_required
def CrearUsuariosView(request):
    data = {}
    if request.method == 'POST':
        form = CargueUsuarios(request.POST, request.FILES)
        if form.is_valid():
            users = []
            polizas_medidores = []
            cliente = []
            data = CargueExcel(request.FILES['archivo_usuarios'])
            created_users = CrearUsuarios(request, data)
            for user in created_users[0]:
                usuario = User.objects.get(username=user)
                users.append(usuario)
                polizas_medidores.append(Poliza_Medidor_User.objects.filter(usuario=usuario))
            data = {
                'users' : users,
                'polizas_medidores': polizas_medidores,
                'log': created_users[1],
            }
    else:
        form = CargueUsuarios()
    return render(request, 'pages/crear_usuarios.html', {'form': form,  'data': data})

@login_required
def DetalleUsuarioView(request):

    usuario = request.user
    poliza_medidores = Poliza_Medidor_User.objects.filter(usuario=usuario)

    data = {
        'usuario': usuario,
        'poliza_medidores': poliza_medidores,
    }

    return render(request, 'users/user_detail.html', {'data': data})

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
