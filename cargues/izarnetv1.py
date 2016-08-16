# -*- coding: utf-8 -*-
import pandas as pd
import MySQLdb
from datetime import datetime

conn = MySQLdb.connect(host='localhost',
                  user='root',
                  passwd='root',
                  db='hidromed')

cursor = conn.cursor()

def CargueExcel(archivo):
	return pd.read_excel(archivo)

def CargueRegistros(data):
	headers = []
	add_partial = ('INSERT INTO izarnetv1_izarnetv1 '
		'(fecha, volumen, consumo, volumen_litros, caudal, alarma) ')

	for header in list(data.columns.values):
		headers.append(header)

	for row in data.iterrows():
		fecha = row[1][headers[0]]
		volumen = row[1][headers[1]]
		consumo = row[1][headers[2]]
		volumen_litros = volumen*1000
		caudal = volumen_litros*60
		alarma = row[1][headers[5]]

		datetime.strptime(fecha, '%d/%m/%Y %H:%M')
		print fecha

		add_row = add_partial + ('VALUES ({}, {}, {}, {}, {}, {})'.format(
			fecha, volumen, consumo, volumen_litros, caudal, alarma))
		print add_row
		#cursor.execute(add_row)

	conn.commit()
	cursor.close()
	conn.close()

data = CargueExcel('InfoC11LA004183_Pre.xls')
CargueRegistros(data)