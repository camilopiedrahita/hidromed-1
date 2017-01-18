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

#normalizacion de datos
def normalize(data):

	#normalizar nan
	data = data.fillna(0)

	#normalizar fecha
	data['Marca de tiempo'] = pd.to_datetime(
		data['Marca de tiempo'],
		format='%d/%m/%y %I:%M %p')

	#ordernar por fecha
	data = data.sort_values('Marca de tiempo')

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
	data = normalize(data)
	
	#cargar registros a db
	CargueRegistros(data, file)

	#mover archivo
	if not os.path.exists('Procesados/'):
		os.makedirs('Procesados/')
	shutil.move(file, 'Procesados/' + file)

#cerrar conexion
cursor.close()
conn.close()
