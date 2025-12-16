# Importar librerías necesarias
import pandas as pd
import os
import openpyxl

# Definir rutas de archivos
BASE_DIR = r"C:\Users\demo.user\Desktop\RPA\Desallocate\Excels"

SO_PATH    = os.path.join(BASE_DIR, "SO.xlsx")
OPEN1_PATH = os.path.join(BASE_DIR, "OpenSO1.xlsx")
OPEN2_PATH = os.path.join(BASE_DIR, "OpenSO2.xlsx")

# Crear Archivo SO vacío
v = pd.DataFrame()
v.to_excel(SO_PATH, index=False)

# Verificar existencia de archivos
archivo1_existe = os.path.exists(OPEN1_PATH)
archivo2_existe = os.path.exists(OPEN2_PATH)

# Traer archivos correspondientes
if archivo1_existe:
    SO1 = pd.read_excel(OPEN1_PATH, sheet_name="Data")
else:
    SO1 = pd.DataFrame()

if archivo2_existe:
    SO2 = pd.read_excel(OPEN2_PATH, sheet_name="Data")
else:
    SO2 = pd.DataFrame()

SO = pd.read_excel(SO_PATH, sheet_name="Sheet1")

# Verificar columnas y tipos de datos
if archivo1_existe:
    print("SO1 columnas:", SO1.columns.tolist())
    SO1 = SO1[sorted(SO1.columns)]

    if archivo2_existe:
        print("SO2 columnas:", SO2.columns.tolist())
        SO2 = SO2[sorted(SO2.columns)]

        # Verificar diferencias de tipos de datos
        print((SO1.dtypes == SO2.dtypes).value_counts())
        print("Diferencias en tipos de datos:")
        print(SO1.dtypes.compare(SO2.dtypes))

        # Cambiar manualmente tipos de dato según columnas diferentes entre df de tipos de datos
        if 'Del. Block Header' in SO2.columns:
            SO2['Del. Block Header'] = SO2['Del. Block Header'].astype(str)

        if 'Sold-to PO Item' in SO2.columns:
            SO2['Sold-to PO Item'] = SO2['Sold-to PO Item'].astype('Int64')
        if 'Sold-to PO Item' in SO1.columns:
            SO1['Sold-to PO Item'] = SO1['Sold-to PO Item'].astype('Int64')

else:
    # Si no existe SO1, usar SO2 si existe, o dejar SO vacío
    if archivo2_existe:
        print("SO2 columnas:", SO2.columns.tolist())
        SO2 = SO2[sorted(SO2.columns)]
        if 'Sold-to PO Item' in SO2.columns:
            SO2['Sold-to PO Item'] = SO2['Sold-to PO Item'].astype('Int64')

# Concatenar archivos (si existen)
if archivo1_existe and archivo2_existe:
    SO = pd.concat([SO1, SO2], ignore_index=True)
elif archivo1_existe and not archivo2_existe:
    SO = SO1.copy()
elif not archivo1_existe and archivo2_existe:
    SO = SO2.copy()
else:
    SO = pd.DataFrame()

# Guardar el resultado
SO.to_excel(SO_PATH, index=False)