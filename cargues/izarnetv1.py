import pandas as pd
import MySQLdb
from datetime import datetime
import glob
import shutil

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
	get_procesados = ('SELECT id FROM izarnetv1_izarnetv1procesados '
		'WHERE nombre = "{}"'.format(file_name))
	cursor.execute(get_procesados)
	procesado_id = cursor.fetchone()
	if procesado_id == None:
		add_procesados_partial = ('INSERT INTO izarnetv1_izarnetv1procesados '
			'(nombre, fecha, estado) ')
		estado = 'Cargue correcto'
		parsed_file_name = file_name.split('_')[1]
		add_partial = ('INSERT INTO izarnetv1_izarnetv1 '
			'(fecha, volumen, consumo, volumen_litros, caudal, alarma, medidor_id) ')
		get_medidor = ('SELECT id FROM medidores_medidor '
			'WHERE serial = "{}"'.format(parsed_file_name))
		cursor.execute(get_medidor)
		medidor_id = cursor.fetchone()
		if medidor_id == None:
			Log('No existe el medidor {}'.format(parsed_file_name))
			medidor_id = None
			estado = 'Cargue con errores'
		else:	
			medidor_id = medidor_id[0]
		for header in list(data.columns.values):
			headers.append(header)

		for row in data.iterrows():
			try:
				fecha = row[1][headers[0]]
				fecha = datetime.strptime(fecha, '%d/%m/%y %I:%M %p')
				volumen = float(str(row[1][headers[1]]).replace(',', '.'))
				consumo = float(str(row[1][headers[2]]).replace(',', '.'))
				volumen_litros = volumen*1000
				caudal = 0
				alarma = u'%s' % row[1][headers[4]]
				alarma = alarma.encode('ascii', 'ignore')
				add_row = add_partial + ('VALUES ("{}", {}, {}, {}, {}, "{}", {})'.
					format(fecha, volumen, consumo, volumen_litros, 
						caudal, alarma, medidor_id))
				try:
					cursor.execute(add_row)
				except Exception, e:
					Log(str(e))
					Log('Error en {}'.format(add_row))
					Log('Error en archivo {}'.format(parsed_file_name))
					estado = 'Cargue con errores'
			except Exception, e:
				Log(str(e))
				Log('Error en Headers del archivo Excel')
				Log('Error en archivo {}'.format(parsed_file_name))
				estado = 'Cargue con errores'
		
		add_procesados = add_procesados_partial + ('VALUES ("{}", "{}", "{}")'.
			format(file_name, 
				datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 
				estado))
		cursor.execute(add_procesados)
		conn.commit()
		print 'Se han cargado todos los datos'
	else:
		Log('El archivo {} ya ha sido procesado anteriormente'.format(file_name))

path = ''
file_names = glob.glob(path + 'IzarNet1*.xls')
for file in file_names:
	print file
	data = CargueExcel(file)
	CargueRegistros(data, file)
	shutil.move(file, 'Procesados/' + file)

cursor.close()
conn.close()