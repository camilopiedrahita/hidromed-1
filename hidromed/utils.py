import pandas as pd

def CargueExcel(archivo):
	return pd.ExcelFile(archivo)