import os
import re
from datetime import datetime, timedelta

ruta_base = r"\\103.20.120\80 - Stock Assignation"
patron_fecha = re.compile(r"(\d{1,2})\s*\.\s*(\d{1,2})\s*\.\s*(\d{4})")

# Determinar fecha actual
hoy = datetime.today()

# Definir rango de fechas: 2 días antes y 5 días después
fecha_inicio = hoy - timedelta(days=2)
fecha_fin = hoy + timedelta(days=5)

def generar_nombre(fecha_dt):
    fecha_norm = fecha_dt.strftime("%d.%m.%Y")
    return f"2-SubsStockAllocation-Lite-{fecha_norm}.xlsb"

print(f"Fecha actual (hoy): {hoy.strftime('%d.%m.%Y')}")
print(f"Fecha inicio (2 dias antes): {fecha_inicio.strftime('%d.%m.%Y')}")
print(f"Fecha fin (5 dias despues): {fecha_fin.strftime('%d.%m.%Y')}")

for nombre_original in os.listdir(ruta_base):
    if not nombre_original.lower().endswith(".xlsb"):
        continue

    match_fecha = patron_fecha.search(nombre_original)
    if not match_fecha:
        print(f"No se encontro fecha en: {nombre_original}")
        continue

    dia, mes, anio = match_fecha.groups()
    try:
        dia = f"{int(dia):02d}"
        mes = f"{int(mes):02d}"
        fecha_str = f"{dia}.{mes}.{anio}"
        fecha_dt = datetime.strptime(fecha_str, "%d.%m.%Y")
    except ValueError:
        print(f"Fecha invalida en: {nombre_original}")
        continue

    if not (fecha_inicio <= fecha_dt <= fecha_fin):
        print(f"Archivo fuera de rango: {nombre_original} (fecha: {fecha_dt.strftime('%d.%m.%Y')})")
        continue

    nuevo_nombre = generar_nombre(fecha_dt)
    ruta_original = os.path.join(ruta_base, nombre_original)
    ruta_nueva = os.path.join(ruta_base, nuevo_nombre)

    if nombre_original == nuevo_nombre:
        print(f"Ya correcto: {nombre_original}")
        continue

    if os.path.exists(ruta_nueva):
        print(f"Destino ya existe, NO renombrado: {nombre_original} -> {nuevo_nombre}")
        continue

    try:
        os.rename(ruta_original, ruta_nueva)
        print(f"Renombrado: {nombre_original} -> {nuevo_nombre}")
    except Exception as e:
        print(f"Error renombrando {nombre_original} -> {nuevo_nombre}: {e}")