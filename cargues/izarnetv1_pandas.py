import os
import glob
import shutil
import MySQLdb
import pandas as pd
from datetime import datetime

#crear conexion a db
conn = MySQLdb.connect(host='localhost',
                  user='root',
                  passwd='root',
                  db='hidromed')
cursor = conn.cursor()

#convertir excel en dataframe
def CargueExcel(archivo):
	return pd.read_excel(archivo)

#funcion para crer log de errores
def Log(mensaje):
	file_log = open(str(datetime.now().
		strftime("%Y-%m-%d")) + '_log','a')
	file_log.write(mensaje + '\n')
	file_log.close()

#cargue de datos a db
def CargueRegistros(data, file_name):
	print (data)

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

#cerrar conexion
cursor.close()
conn.close()
