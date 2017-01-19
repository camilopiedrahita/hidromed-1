import os
import glob
import shutil
import pandas as pd
import mysql.connector
from datetime import datetime
from sqlalchemy import create_engine

#crear conexion a db
engine = create_engine(
	'mysql+mysqlconnector://root:root@localhost/hidromed', echo=False)

#convertir excel en dataframe
def CargueExcel(archivo):
	return pd.read_excel(archivo)

#funcion para crer log de errores
def Log(mensaje):
	file_log = open(str(datetime.now().
		strftime("%Y-%m-%d")) + '_log','a')
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


#cargue de datos a db
def CargueRegistros(data, file_name):

	#get medidor id
	data['medidor_id'] = MedidorId(file_name)

	#enviar data a db
	try:
		data.to_sql(name='izarnet_izarnet', con=engine, if_exists = 'append', index=False)
		print ('data cargada correctamente')
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

	#normalizar fecha
	data['Marca de tiempo'] = pd.to_datetime(
		data['Marca de tiempo'],
		format='%d/%m/%y %I:%M %p')

	#ordernar por fecha
	data = data.sort_values('Marca de tiempo')

	#obtener headers del archivo
	for header in list(data.columns.values):
		headers.append(header)

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
path = ''
file_names = glob.glob(path + 'IzarNet1*.xls')
for file in file_names:

	#inicio del cargue
	print (file)

	#cargar archivo excel
	data = CargueExcel(file)

	#normalizar data
	data = Normalize(data)
	
	#cargar registros a db
	CargueRegistros(data, file)

	#mover archivo
	if not os.path.exists('Procesados/'):
		os.makedirs('Procesados/')
	#shutil.move(file, 'Procesados/' + file)
