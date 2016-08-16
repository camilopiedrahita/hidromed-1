# -*- coding: utf-8 -*-
import pandas as pd
import MySQLdb

conn = MySQLdb.connect(host='localhost',
                  user='root',
                  passwd='root',
                  db='hidromed')

cursor = conn.cursor()

def CargueExcel(archivo):
	return pd.read_excel(archivo)

def CargueRegistros(data):
	headers = []
	for header in list(data.columns.values):
		headers.append(header)

	cuenta = 0
	for row in data.iterrows():
		tiempo = row[1][headers[1]]
		volumen = row[1][headers[2]]
		consumo = row[1][headers[3]]
		volumen_litros = volumen*1000
		caudal = volumen_litros*60
		alarma = row[1][headers[5]]
		cuenta += 1
		print (str(cuenta) + ' ' +
			str(tiempo) + ' ' +
			str(volumen) + ' ' +
			str(consumo) + ' ' +
			str(volumen_litros) + ' ' +
			str(caudal) + ' ' +
			alarma + ' ')


data = CargueExcel('InfoC11LA004183_Pre.xls')
CargueRegistros(data)