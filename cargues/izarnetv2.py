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
		strftime("%Y-%m-%d %H:%M")) + '_log','a')
	file_log.write(mensaje + '\n')
	file_log.close()

def CargueRegistros(data, file_name):
	#Queries partials
	get_procesados = ('SELECT id FROM izarnet_izarnetprocesados '
		'WHERE nombre = "{}"'.format(file_name))
	add_procesados_partial = ('INSERT INTO izarnet_izarnetprocesados '
		'(nombre, fecha, estado) ')
	add_partial = ('INSERT INTO izarnet_izarnet '
		'(fecha, volumen, consumo, volumen_litros, caudal, alarma, medidor_id, consumo_acumulado) ')
	get_medidor_partial = ('SELECT id FROM medidores_medidor ')
	last_id_partial = ('SELECT MAX(id) FROM izarnet_izarnet ')
	last_fecha_partial = ('SELECT fecha FROM izarnet_izarnet ')
	last_consumo_acumulado_partial = ('SELECT consumo_acumulado FROM izarnet_izarnet ')

	headers = []
	cursor.execute(get_procesados)
	procesado_id = cursor.fetchone()
	if procesado_id == None:
		estado = 'Cargue correcto'
		parsed_file_name = file_name.split('_')[1]
		get_medidor = get_medidor_partial + (
			'WHERE serial = "{}"'.format(parsed_file_name))
		cursor.execute(get_medidor)
		medidor_id = cursor.fetchone()
		if medidor_id == None:
			Log('No existe el medidor {}'.format(parsed_file_name))
			estado = 'Cargue con errores'
		else:	
			medidor_id = medidor_id[0]
			last_id = last_id_partial + (
				'WHERE medidor_id = "{}"'.format(medidor_id))
		for header in list(data.columns.values):
			headers.append(header)

		for row in data.iterrows():
			try:
				fecha = row[1][headers[0]]
				fecha = datetime.strptime(str(fecha), '%Y-%m-%d %H:%M:%S')
				volumen_litros = float(str(row[1][headers[1]]).replace(',', '.'))
				consumo = float(str(row[1][headers[2]]).replace(',', '.'))
				volumen = volumen_litros/1000
				alarma = u'%s' % row[1][headers[4]]
				alarma = alarma.encode('ascii', 'ignore')
				cursor.execute(last_id)
				last_medidor_data = cursor.fetchone()
				last_medidor_data = last_medidor_data[0]
				if last_medidor_data == None:
					caudal = 0
					consumo_acumulado = 0
				else:
					last_fecha = last_fecha_partial + (
						'WHERE id = "{}"'.format(last_medidor_data))
					cursor.execute(last_fecha)
					last_fecha_data = cursor.fetchone()
					last_fecha_data = last_fecha_data[0]
					if (fecha - last_fecha_data).total_seconds() < 0:
						minutos = (((fecha - last_fecha_data)*-1).total_seconds())/60
					else:
						minutos = ((fecha - last_fecha_data).total_seconds())/60
					caudal = consumo / minutos * 60
					last_consumo_acumulado = last_consumo_acumulado_partial + (
						'WHERE id = "{}"'.format(last_medidor_data))
					cursor.execute(last_consumo_acumulado)
					last_consumo_acumulado_data = cursor.fetchone()
					last_consumo_acumulado_data = last_consumo_acumulado_data[0]
					consumo_acumulado = last_consumo_acumulado_data + consumo

				add_row = add_partial + ('VALUES ("{}", {}, {}, {}, {}, "{}", {}, {})'.
					format(fecha, volumen, consumo, volumen_litros, 
						caudal, alarma, medidor_id, consumo_acumulado))
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
	#shutil.move(file, 'Procesados/' + file)

cursor.close()
conn.close()