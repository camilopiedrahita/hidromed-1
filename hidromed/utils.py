# -*- coding: utf-8 -*-
import pandas as pd

def CargueExcel(archivo):
	return pd.read_excel(archivo, converters={
		'Serial Medidor': lambda x: str(x),
		'Póliza': lambda x: str(x)})
