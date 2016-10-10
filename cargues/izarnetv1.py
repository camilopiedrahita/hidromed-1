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
	return pd.read_excel(archivo)

def Log(mensaje):
	file_log = open(str(datetime.now().
		strftime("%Y-%m-%d %H:%M")) + '_log','a')
	file_log.write(mensaje + '\n')
	file_log.close()

def RecalcData(id_desde, id_hasta, last):
	data_partial = ('SELECT id, caudal, consumo, consumo_acumulado, fecha FROM izarnet_izarnet '
		'WHERE id >= {} AND id < {} ORDER BY fecha;'.format(id_desde, id_hasta))
	initial_partial = ('SELECT id, caudal, consumo, consumo_acumulado, fecha FROM izarnet_izarnet '
		'WHERE fecha = "{}";'.format(last))
	cursor.execute(data_partial)
	data = cursor.fetchall()
	cursor.execute(initial_partial)
	initial = cursor.fetchone()
	last_consumo_acumulado = initial[3]
	last_fecha = initial[4]

	for registro in data:
		id = registro[0]
		new_caudal = registro[1]
		new_consumo = registro[2]
		new_consumo_acumulado = registro[3]
		new_fecha = registro[4]
		if (new_fecha - last_fecha).total_seconds() < 0:
			minutos = (((new_fecha - last_fecha)*-1).total_seconds())/60
		else:
			minutos = ((new_fecha - last_fecha).total_seconds())/60
		caudal = new_consumo * 1000 / minutos * 60
		consumo_acumulado = last_consumo_acumulado + new_consumo
		udpate = ('UPDATE izarnet_izarnet SET '
			'caudal = {}, ' 
			'consumo_acumulado = {} '
			'WHERE id = {};'.format(
				caudal,
				consumo_acumulado,
				id))
		cursor.execute(udpate)
		last_consumo_acumulado = consumo_acumulado
		last_fecha = new_fecha
	conn.commit()	

def CargueRegistros(data, file_name):
	#Queries partials
	add_procesados_partial = ('INSERT INTO izarnet_izarnetprocesados '
		'(nombre, fecha, estado) ')
	add_partial = ('INSERT INTO izarnet_izarnet '
		'(fecha, volumen, consumo, volumen_litros, caudal, alarma, medidor_id, consumo_acumulado) ')
	get_medidor_partial = ('SELECT id FROM medidores_medidor ')
	last_id_partial = ('SELECT MAX(id) FROM izarnet_izarnet ')
	last_fecha_partial = ('SELECT fecha FROM izarnet_izarnet ')
	last_consumo_acumulado_partial = ('SELECT consumo_acumulado FROM izarnet_izarnet ')
	id_match_partial = ('SELECT id FROM izarnet_izarnet ')
	min_id_partial = ('SELECT MIN(id) FROM izarnet_izarnet ')
	id_hasta_partial = ('SELECT id FROM izarnet_izarnet ')

	headers = []
	recalcular = False
	id_found = None
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
	for header in list(data.columns.values):
		headers.append(header)

	for row in data.iterrows():
		try:
			fecha = row[1][headers[0]]
			fecha = datetime.strptime(str(fecha), '%Y-%m-%d %H:%M:%S')
			volumen = float(str(row[1][headers[1]]).replace(',', '.'))
			consumo = float(str(row[1][headers[2]]).replace(',', '.'))
			volumen_litros = volumen*1000
			alarma = u'%s' % row[1][headers[4]]
			alarma = alarma.encode('ascii', 'ignore')
			min_id = min_id_partial + (
				'WHERE medidor_id = "{}" AND fecha > "{}"'.format(
					medidor_id, str(fecha)))
			cursor.execute(min_id)
			min_id_data = cursor.fetchone()
			min_id_data = min_id_data[0]
			if not min_id_data == None and recalcular == False:
				id_desde = min_id_data
				fecha_hasta = fecha
				id_found = False
				recalcular = True
			last_id = last_id_partial + (
				'WHERE medidor_id = "{}" AND fecha < "{}"'.format(
					medidor_id, str(fecha)))
			cursor.execute(last_id)
			last_medidor_data = cursor.fetchone()
			last_medidor_data = last_medidor_data[0]
			id_match = id_match_partial + (
				'WHERE fecha = "{}"'.format(str(fecha)))
			cursor.execute(id_match)
			id_match_data = cursor.fetchone()
			if not id_match_data == None:
				id_match_data = id_match_data[0]
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
				caudal = consumo * 1000 / minutos * 60
				last_consumo_acumulado = last_consumo_acumulado_partial + (
					'WHERE id = "{}"'.format(last_medidor_data))
				cursor.execute(last_consumo_acumulado)
				last_consumo_acumulado_data = cursor.fetchone()
				last_consumo_acumulado_data = last_consumo_acumulado_data[0]
				consumo_acumulado = last_consumo_acumulado_data + consumo
			if id_match_data == None:
				add_row = add_partial + ('VALUES ("{}", {}, {}, {}, {}, "{}", {}, {})'.
					format(fecha, volumen, consumo, volumen_litros, 
						caudal, alarma, medidor_id, consumo_acumulado))
				last = fecha
			else:
				add_row = ('UPDATE izarnet_izarnet SET '
					'fecha = "{}", ' 
					'volumen = {}, '
					'consumo = {}, '
					'volumen_litros = {}, '
					'caudal = {}, '
					'alarma = "{}", '
					'medidor_id = {}, '
					'consumo_acumulado = {} '
					'WHERE id = {};'.format(
						fecha,
						volumen,
						consumo,
						volumen_litros,
						caudal,
						alarma,
						medidor_id,
						consumo_acumulado,
						id_match_data))
				last = fecha
			try:
				cursor.execute(add_row)
				if id_found == False:
					id_found = True
					id_hasta = id_hasta_partial + (
						'WHERE '
						'fecha = "{}" AND '
						'volumen = {} AND '
						'consumo = {} AND '
						'volumen_litros = {} AND '
						'caudal = {} AND '
						'alarma = "{}" AND '
						'medidor_id = {} AND '
						'consumo_acumulado = {};'.format(
							fecha,
							volumen,
							consumo,
							volumen_litros,
							caudal,
							alarma,
							medidor_id,
							consumo_acumulado))
					cursor.execute(id_hasta)
					id_hasta_data = cursor.fetchone()
					id_hasta_data = id_hasta_data[0]
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
			datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 
			estado))
	cursor.execute(add_procesados)
	conn.commit()
	if recalcular == True:
		RecalcData(id_desde, id_hasta_data, last)
	print 'Se han cargado todos los datos'
	
path = ''
file_names = glob.glob(path + 'IzarNet1*.xls')
for file in file_names:
	print file
	data = CargueExcel(file)
	data = data.fillna(0)
	data['Marca de tiempo'] = pd.to_datetime(
		data['Marca de tiempo'],
		format='%d/%m/%y %I:%M %p')
	data = data.sort_values('Marca de tiempo')
	CargueRegistros(data, file)
	shutil.move(file, 'Procesados/' + file)

cursor.close()
conn.close()
