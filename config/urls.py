# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic import TemplateView
from django.views import defaults as default_views

from hidromed.users import views as views_users
from hidromed.graficas import views as views_graficas
from hidromed.tablero import views as views_tablero
from hidromed.medidores import views as views_medidores
from hidromed.alarmas import views as views_alarmas

from allauth.account import views as views_allauth

urlpatterns = [
    url(r'^$', views_allauth.login),
    url(r'^home/$', TemplateView.as_view(template_name='pages/home.html'), name='home'),
    url(r'^about/$', TemplateView.as_view(template_name='pages/about.html'), name='about'),

    # Django Admin, use {% url 'admin:index' %}
    url(settings.ADMIN_URL, include(admin.site.urls)),

    # User management
    url(r'^users/', include('hidromed.users.urls', namespace='users')),
    url(r'^accounts/', include('allauth.urls')),

    # Your stuff: custom urls includes go here
    url(r'^detalle_usuario/', views_users.DetalleUsuarioView, name='detalle_usuario'),
    url(r'^crear-usuarios', views_users.CrearUsuariosView, name='crear_usuarios'),

    #graficos
    url(r'^gratis', views_graficas.FreeChartView, name='grafica_gratis'),

    #descargar excel
    url(
        r'^descargar-excel/(?P<medidor>[\w-]+)/(?P<desde>\d+-\d+-\d+\ \d+:\d+:\d+)/(?P<hasta>\d+-\d+-\d+\ \d+:\d+:\d+)/(?P<periodo_datos>[-\w]+)/(?P<tipo_de_grafico>[\w-]+)/$',
        views_graficas.DownloadExcel,
        name='descargar_excel'),

    #tablero rapido
    url(r'^tablero_rapido/$', views_tablero.TablerRapidoView, name='tablero_rapido'),

    #alarmas
    url(r'^alarmas/$', views_alarmas.UltimoMesView, name='alarmas'),    

    #admin_medidores
    url(r'^medidores', views_medidores.MedidoresView, name='medidores'),
    url(r'^ajax/load_medidores/$', views_medidores.LoadMedidorView, name='load_medidores'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        url(r'^400/$', default_views.bad_request, kwargs={'exception': Exception('Bad Request!')}),
        url(r'^403/$', default_views.permission_denied, kwargs={'exception': Exception('Permission Denied')}),
        url(r'^404/$', default_views.page_not_found, kwargs={'exception': Exception('Page not Found')}),
        url(r'^500/$', default_views.server_error),
    ]
