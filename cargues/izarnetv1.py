import pandas as pd
import MySQLdb
from datetime import datetime
import glob

conn = MySQLdb.connect(host='localhost',
                  user='root',
                  passwd='root',
                  db='hidromed')

cursor = conn.cursor()

def CargueExcel(archivo):
	return pd.read_excel(archivo)

def Log(mensaje):
	file_log = open(str(datetime.now().
		strftime("%Y-%m-%d %H:%M")) + '_log','a')
	file_log.write(mensaje + '\n')
	file_log.close()

def CargueRegistros(data, file_name):
	headers = []
	file_name = file_name.replace('Info', '')
	file_name = file_name.replace('_Pre.xls', '')
	add_partial = ('INSERT INTO izarnetv1_izarnetv1 '
		'(fecha, volumen, consumo, volumen_litros, caudal, alarma, medidor_id) ')
	get_medidor = ('SELECT id FROM medidores_medidor '
		'WHERE serial = "{}"'.format(file_name))
	cursor.execute(get_medidor)
	medidor_id = cursor.fetchone()
	if medidor_id == None:
		Log('No existe el medidor {}'.format(file_name))
		medidor_id = None
	else:	
		medidor_id = medidor_id[0]
	for header in list(data.columns.values):
		headers.append(header)

	for row in data.iterrows():
		fecha = row[1][headers[0]]
		fecha = datetime.strptime(fecha, '%d/%m/%y %I:%M %p')
		volumen = row[1][headers[1]]
		consumo = row[1][headers[2]]
		volumen_litros = volumen*1000
		caudal = volumen_litros*60
		alarma = row[1][headers[5]]
		alarma = alarma.encode('ascii', 'ignore')
		add_row = add_partial + ('VALUES ("{}", {}, {}, {}, {}, "{}", {})'.
			format(fecha, volumen, consumo, volumen_litros, 
				caudal, alarma, medidor_id))
		try:
			cursor.execute(add_row)
		except Exception, e:
			Log(str(e))
			Log('Error en {}'.format(add_row))
			Log('Error en archivo {}'.format(file_name))
		
	conn.commit()
	cursor.close()
	conn.close()
	print 'Se han cargado todos los datos'

path = ''
file_names = glob.glob(path + '*.xls')
for file in file_names:
	data = CargueExcel(file)
	CargueRegistros(data, file)