import sys
import xlsxwriter
from datetime import datetime, timedelta
import xlwings as xw
import pandas as pd
import numpy as np
import os
os.environ["MPLBACKEND"] = "Agg"

ruta_so_txt = r"C:\Users\g\reallocation-\so.txt"
ruta_mat_txt = r"C:\Users\g\reallocation-\mat.txt"

if os.path.exists(ruta_so_txt):
    os.remove(ruta_so_txt)
if os.path.exists(ruta_mat_txt):
    os.remove(ruta_mat_txt)

try:
    with open(ruta_so_txt, "w") as f:
        pass
    with open(ruta_mat_txt, "w") as f:
        pass
except OSError as e:
    print(f"Error creating files: {e}")


def normalizar(nombre):
    return nombre.strip().lower().replace(" ", "").replace("\n", "")

def main():
    carpeta = r"\\103.20.120\80 - Stock Assignation"
    hoy = datetime.now()
    dia_semana = hoy.weekday()  # Lunes=0, Domingo=6
    hora_actual = hoy.hour

    # Calcular fecha base según día de la semana (sin ajuste horario)
    if dia_semana <= 3:  # Lunes(0) a Jueves(3)
        base_fecha_target = hoy + timedelta(days=1)
    elif dia_semana == 4:  # Viernes(4)
        base_fecha_target = hoy + timedelta(days=3)
    elif dia_semana == 5:  # Sábado(5)
        base_fecha_target = hoy + timedelta(days=2)
    else:  # Domingo(6)
        base_fecha_target = hoy + timedelta(days=1)

    # Ajuste por hora:
    if hora_actual >= 16:
        fecha_target = base_fecha_target  # Usa la fecha base calculada
    else:
        fecha_target = hoy   # Usa la fecha de ayer

    fecha_formateada = fecha_target.strftime("%d.%m.%Y")
    nombre_archivo = f"2-SubsStockAllocation-Lite-{fecha_formateada}.xlsb"
    ruta_completa = os.path.join(carpeta, nombre_archivo)

    print(ruta_completa)  # Opcional: verificación de ruta

    fecha_formateada = fecha_target.strftime("%d.%m.%Y")
    nombre_archivo = f"2-SubsStockAllocation-Lite-{fecha_formateada}.xlsb"
    ruta_completa = os.path.join(carpeta, nombre_archivo)

    if not os.path.exists(ruta_completa):
        print(f" Archivo no encontrado: {ruta_completa}")
        sys.exit(0)

    try:
        app = xw.App(visible=False)
        app.display_alerts = False
        app.screen_updating = False

        wb = app.books.open(ruta_completa)
        print("Archivo abierto en segundo plano: {ruta_completa}")

        hoja = wb.sheets["+Sorting"]
        df = hoja.used_range.options(pd.DataFrame, header=1, index=False).value

        df.columns = [normalizar(col) for col in df.columns]
        df_filtrado = df[
            (df["partnertype"] == "Subsidiary")
            & (df["finalactionstatus"] == "Proceed with DO")
        ]

        so = df_filtrado["s/o"].tolist()
        mat = df_filtrado["cust.material"].tolist()

        with open(ruta_so_txt, "w", encoding="utf-8") as file_so:
            for s in so:
                file_so.write(f"{s}\n")

        with open(ruta_mat_txt, "w", encoding="utf-8") as file_mat:
            for m in mat:
                file_mat.write(f"{m}\n")

        print(" Listas generadas y guardadas en archivos de texto.")

        wb.close()
        app.quit()
        print(" Libro cerrado y Excel terminado.")

    except Exception as e:
        print(f" Error al manejar el archivo: {e}")
if __name__ == "__main__":
    main()