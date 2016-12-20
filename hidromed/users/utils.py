# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import numpy as np

from django.contrib import messages

from .models import *

from hidromed.empresas.models import Acueducto, Cliente
from hidromed.medidores.models import Medidor, Medidor_Cliente, Medidor_Acueducto
from hidromed.polizas.models import Poliza, Poliza_Cliente, Poliza_Acueducto

#Crear usuarios a partir de data source
def CrearUsuarios(request, data):
	created_users = []
	data = data.replace(np.nan, ' ', regex=True)
	correcto = True
	log = []
	for row in data.iterrows():
		creation_error = False
		nit_acueducto = row[1]['ID NIT Acueducto']
		acueducto = row[1]['Acueducto']
		poliza = row[1]['Póliza']
		serial = row[1]['Serial Medidor']
		cliente = row[1]['Cliente']
		nit_cc_cliente = row[1]['Nit/CC Cliente']
		direccion_cliente = row[1]['Dirección Cliente']
		username = row[1]['Usuario Acceso'].replace(' ', '')
		username = username.lower()
		if (serial == ' ' or 
			cliente == ' ' or
			nit_cc_cliente == ' ' or 
			direccion_cliente == ' ' or
			username == ' ' or
			nit_acueducto == ' ' or
			acueducto == ' '):
			correcto = False
		else:
			if Acueducto.objects.filter(nit=nit_acueducto):
				acueducto_id = Acueducto.objects.get(nit=nit_acueducto)
			else:
				acueducto_id = Acueducto.objects.create(
					nombre=acueducto,
					nit=nit_acueducto)
			if Poliza.objects.filter(numero=poliza):
				poliza_id = Poliza.objects.get(numero=poliza)
			else:
				poliza_id = Poliza.objects.create(
					numero=poliza)
			if Medidor.objects.filter(serial=serial):
				medidor_id = Medidor.objects.get(serial=serial)
			else:
				medidor_id = Medidor.objects.create(
					serial=serial)
			if Cliente.objects.filter(nit=nit_cc_cliente):
				cliente_id = Cliente.objects.get(nit=nit_cc_cliente)
			else:
				cliente_id = Cliente.objects.create(
					nombre=cliente,
					nit=nit_cc_cliente,
					direccion=direccion_cliente)
			if User.objects.filter(username=username):
				user_id = User.objects.get(username=username)
			else:
				user_id = User.objects.create_user(
					username,
					'',
					'Hidromed')
				user_id.cliente = cliente_id
				user_id.perfil = 0
				user_id.save()
			if not Poliza_Cliente.objects.filter(poliza=poliza_id):
				Poliza_Cliente.objects.create(poliza=poliza_id, cliente=cliente_id)
			else:
				poliza_cliente_id = Poliza_Cliente.objects.get(poliza=poliza_id)
				if not poliza_cliente_id.cliente == cliente_id:
					creation_error = True
					log.append(
						'La póliza ' + str(poliza) + ' ya está asignada a un cliente')
			if not Poliza_Acueducto.objects.filter(poliza=poliza_id):
				Poliza_Acueducto.objects.create(poliza=poliza_id,
					acueducto=acueducto_id)
			else:
				poliza_acueducto_id = Poliza_Acueducto.objects.get(
					poliza=poliza_id)
				if not poliza_acueducto_id.acueducto == acueducto_id:
					creation_error = True
					log.append(
						'La póliza ' + str(poliza) + ' ya está asignada a un acueducto')
			if not Medidor_Cliente.objects.filter(medidor=medidor_id):
				Medidor_Cliente.objects.create(medidor=medidor_id,
					cliente=cliente_id)
			else:
				medidor_cliente_id = Medidor_Cliente.objects.get(
					medidor=medidor_id)
				if not medidor_cliente_id.cliente == cliente_id:
					creation_error = True
					log.append(
						'El medidor ' + str(serial) + ' ya está asignado a un cliente')
			if not Medidor_Acueducto.objects.filter(medidor=medidor_id):
				Medidor_Acueducto.objects.create(medidor=medidor_id,
					acueducto=acueducto_id)
			else:
				medidor_acueducto_id = Medidor_Acueducto.objects.get(
					medidor=medidor_id)
				if not medidor_acueducto_id.acueducto == acueducto_id:
					creation_error = True
					log.append(
						'El medidor ' + str(serial) + ' ya está asignado a un acueducto')
			if Poliza_Medidor_User.objects.filter(poliza=poliza_id, 
				usuario=user_id, medidor=medidor_id):
				log.append(
					'El usuario ' + str(username) + ' ya tiene asignado '+
					'el medidor ' + str(serial) + ' y la póliza ' +
					str(poliza))
			else:
				if creation_error == False:
					Poliza_Medidor_User.objects.create(
						poliza=poliza_id, 
						medidor=medidor_id,
						usuario=user_id)
					if not any(i == username for i in created_users):
						created_users.append(username)
				else:
					log.append(
						'No se ha completado la asignación de medidores y ' +
						'pólizas al usuario ' + str(username) + 
						'Por favor valide el log de errores')
			if not correcto == False:
				correcto = True
	if correcto == True:
		messages.success(request, 'Proceso terminado')
	else:
		messages.warning(request, 'Valide que los campos estén diligenciados')
	return created_users, log