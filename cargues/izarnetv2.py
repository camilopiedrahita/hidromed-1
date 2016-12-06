import pandas as pd
import MySQLdb
import glob
import shutil
from datetime import datetime

conn = MySQLdb.connect(host='localhost',
                  user='root',
                  passwd='root',
                  db='hidromed')

cursor = conn.cursor()

def CargueExcel(archivo):
	return pd.read_excel(archivo, sheetname=1)

def Log(mensaje):
	file_log = open(str(datetime.now().
		strftime("%Y-%m-%d")) + '_log','a')
	file_log.write(mensaje + '\n')
	file_log.close()

def CargueRegistros(data, file_name):
	#Queries partials
	add_procesados_partial = ('INSERT INTO izarnet_izarnetprocesados '
		'(nombre, fecha, estado) ')
	add_partial = ('INSERT INTO izarnet_izarnet '
		'(fecha, volumen, consumo, volumen_litros, alarma, medidor_id) ')
	get_medidor_partial = ('SELECT id FROM medidores_medidor ')
	id_match_partial = ('SELECT id FROM izarnet_izarnet ')

	#Local vars
	headers = []
	estado = 'Cargue correcto'
	parsed_file_name = file_name.split('_')[1]
	parsed_file_name = parsed_file_name.replace(".xls", "")
	get_medidor = get_medidor_partial + (
		'WHERE serial = "{}"'.format(parsed_file_name))
	cursor.execute(get_medidor)
	medidor_id = cursor.fetchone()
	if medidor_id == None:
		Log('No existe el medidor {}'.format(parsed_file_name))
		Log('Error en archivo {}'.format(file_name))
		estado = 'Cargue con errores'
	else:	
		medidor_id = medidor_id[0]
	for header in list(data.columns.values):
		headers.append(header)

	#Insert Data
	if not medidor_id == None:
		for row in data.iterrows():
			try:
				fecha = row[1][headers[0]]
				fecha = datetime.strptime(str(fecha), '%Y-%m-%d %H:%M:%S')
				volumen_litros = float(str(row[1][headers[1]]).replace(',', '.'))
				consumo = float(str(row[1][headers[2]]).replace(',', '.'))
				if not volumen_litros == 0:
					volumen = volumen_litros/1000
				else:
					volumen = 0
				alarma = u'%s' % row[1][headers[4]]
				alarma = alarma.encode('ascii', 'ignore')

				id_match = id_match_partial + (
					'WHERE fecha = "{}" AND medidor_id = {}'.format(
						str(fecha), medidor_id))
				cursor.execute(id_match)
				id_match_data = cursor.fetchone()
				if not id_match_data == None:
					id_match_data = id_match_data[0]

				if id_match_data == None:
					add_row = add_partial + ('VALUES ("{}", {}, {}, {}, "{}", {})'.
						format(fecha, volumen, consumo, volumen_litros, 
							alarma, medidor_id))
					try:
						cursor.execute(add_row)
					except Exception, e:
						Log(str(e))
						Log('Error en {}'.format(add_row))
						Log('Error en archivo {}'.format(file_name))
						estado = 'Cargue con errores'
			except Exception, e:
				Log(str(e))
				Log('Error en Headers del archivo Excel')
				Log('Error en archivo {}'.format(file_name))
				estado = 'Cargue con errores'
		add_procesados = add_procesados_partial + ('VALUES ("{}", "{}", "{}")'.
			format(file_name, 
				datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 
				estado))
		cursor.execute(add_procesados)
		conn.commit()
		print 'Se han cargado todos los datos'
		
path = ''
file_names = glob.glob(path + 'IzarNet2*.xls')
for file in file_names:
	print file
	data = CargueExcel(file)
	data = data.fillna(0)
	data['event.timestamp'] = pd.to_datetime(
		data['event.timestamp'],
		format='%d-%m-%Y %H:%M:%S')
	data = data.sort_values('event.timestamp')
	CargueRegistros(data, file)
	shutil.move(file, 'Procesados/' + file)

cursor.close()
conn.close()
