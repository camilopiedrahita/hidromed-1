import os
import glob
import shutil
import numpy as np
import pandas as pd
import mysql.connector
from datetime import datetime
from sqlalchemy import create_engine

#crear conexion a db
engine = create_engine(
	'mysql://hidromeddb:wf569KZp5m@localhost/hidromed', echo=False)

#convertir excel en dataframe
def CargueExcel(archivo):
	return pd.read_excel(archivo)

#funcion para crer log de errores
def Log(mensaje):
	file_log = open('/home/hidromedftp/' + str(datetime.now().
		strftime("%Y-%m-%d")) + '_log.log','a')
	file_log.write(mensaje + '\n')
	file_log.close()

#obtener id medidor
def MedidorId(file_name):

	#obtener medidor del archivo
	parsed_file_name = file_name.split('_')[1]
	parsed_file_name = parsed_file_name.replace(".xls", "")

	#obtener id del medidor
	medidor_id = pd.read_sql(
		'SELECT id FROM medidores_medidor WHERE serial = "{}"'.format(parsed_file_name),
		con=engine)

	if not medidor_id.empty:
		medidor_id = medidor_id['id'][0]
	else:
		Log('No existe el medidor {}'.format(parsed_file_name))
		Log('Error en archivo {}'.format(file_name))

	return medidor_id

#registrar estado del cargue
def ArchivoProcesado(file_name, estado):

	#diccionario de data
	data = {
		'nombre': [file_name],
		'fecha': [datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
		'estado': [estado]
	}

	#crear dataframe
	estado_cargue = pd.DataFrame(data)

	#enviar estado a db
	estado_cargue.to_sql(
		name='izarnet_izarnetprocesados', con=engine, if_exists = 'append', index=False)

#flitrar registros ya existentes en db
def RegistrosUnicos(data):

	#declaracion de variables
	medidor_id = data['medidor_id'][0]
	fecha_inicial = data['fecha'].min().to_pydatetime()
	fecha_final = data['fecha'].max().to_pydatetime()

	#obtener datos actuales
	try:
		existing_data = pd.read_sql(
			'SELECT * FROM izarnet_izarnet WHERE medidor_id = %(medidor_id)s ' +
			'AND fecha BETWEEN %(fecha_inicial)s AND %(fecha_final)s',
			params={
				'fecha_final': fecha_final,
				'medidor_id': int(medidor_id),
				'fecha_inicial': fecha_inicial
			},
			con=engine)
		del existing_data['id']

		#concatenar dataframes
		data = [existing_data, data]
		data = pd.concat(data, ignore_index=True)

		#filtrar registros duplicados
		data = data.drop_duplicates(keep=False)

	except Exception, e:
		Log(str(e))
		estado = 'Cargue con errores'
		Log('El Id de medidor no es correcto')

	return data

#cargue de datos a db
def CargueRegistros(data, file_name):

	#get medidor id
	data['medidor_id'] = MedidorId(file_name)

	#filtrar registros ya existentes en db
	data = RegistrosUnicos(data)

	#enviar data a db
	try:
		data.to_sql(
			name='izarnet_izarnet',
			con=engine,
			if_exists = 'append',
			index=False,
			chunksize=1000)
		Log ('data cargada correctamente')
		estado = 'Cargue correcto'
	except Exception, e:
		Log(str(e))
		estado = 'Cargue con errores'
		Log('Error en archivo {}'.format(file_name))

	ArchivoProcesado(file_name, estado)

#conversion de cadena a numero
def FloatNormalize(data):
	try:
		data = float(str(data).replace(',', '.'))
	except Exception, e:
		data = 0
	return data

#normalizacion de alarmas
def AlarmaNormalize(data):
	data = u'%s' % data
	data = data.encode('ascii', 'ignore')
	return data

#normalizacion de datos
def Normalize(data):

	#declaracion de variables
	headers = []

	#normalizar nan
	data = data.fillna(0)

	#obtener headers del archivo
	for header in list(data.columns.values):
		headers.append(header)

	#normalizar fecha
	data[headers[0]] = pd.to_datetime(
		data[headers[0]],
		format='%d/%m/%y %I:%M %p')

	#ordernar por fecha
	data = data.sort_values(headers[0])

	#normalizar tipos de datos
	data[headers[1]] = data[headers[1]].apply(FloatNormalize) #volumen
	data[headers[2]] = data[headers[2]].apply(FloatNormalize) #consumo
	data[headers[4]] = data[headers[4]].apply(AlarmaNormalize) #alarmas
	data['volumen_litros'] = data[headers[1]] * 1000 #volumen a litros
	data[headers[2]] = data[headers[2]] * 1000 #consumo a litros

	#normalizando nombre de columnas
	data = data[[headers[0], headers[1], headers[2], 'volumen_litros', headers[4]]]
	data.columns = ['fecha', 'volumen', 'consumo', 'volumen_litros', 'alarma']

	return data

#main	
path = '/home/hidromedftp/'
file_names = glob.glob(path + 'IzarNet1*.xls')
for file in file_names:

	#inicio del cargue
	Log (file)

	#cargar archivo excel
	data = CargueExcel(file)

	#normalizar data
	data = Normalize(data)
	
	#cargar registros a db
	CargueRegistros(data, file)

	#mover archivo
	if not os.path.exists(path + 'Procesados/'):
		os.makedirs(path + 'Procesados/')
	shutil.move(file, path + 'Procesados/')
