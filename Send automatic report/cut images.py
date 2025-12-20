from PIL import Image
import os

def recortar_imagen(ruta_original, x_plus, x_minus, y_plus, y_minus):
    # Abrir la imagen original
    imagen = Image.open(ruta_original)

    # Obtener dimensiones originales
    ancho_original, alto_original = imagen.size

    # Calcular coordenadas de recorte
    x_inicio = x_plus
    x_fin = ancho_original - x_minus
    y_inicio = y_plus
    y_fin = alto_original - y_minus

    # Verificar que las coordenadas sean válidas
    if x_inicio >= x_fin or y_inicio >= y_fin:
        raise ValueError("Las coordenadas de recorte son inválidas.")

    # Recortar la imagen
    area = (x_inicio, y_inicio, x_fin, y_fin)
    return imagen.crop(area)

def procesar_carpeta(ruta_carpeta, x_plus, x_minus, y_plus, y_minus, rutas_excluidas):
    for archivo in os.listdir(ruta_carpeta):
        ruta_completa = os.path.join(ruta_carpeta, archivo)

        # Solo PNG
        if not archivo.lower().endswith(".png"):
            continue

        # Excluir rutas
        if ruta_completa in rutas_excluidas:
            print(f"Excluyendo: {archivo}")
            continue

        print(f"Procesando: {archivo}")

        try:
            imagen_recortada = recortar_imagen(ruta_completa, x_plus, x_minus, y_plus, y_minus)

            # Sobrescribir el archivo original
            imagen_recortada.save(ruta_completa)
            print(f"Imagen recortada y guardada como: {ruta_completa}")

        except Exception as e:
            print(f"Error al procesar {archivo}: {e}")

# --------------------------------------------------------------------------------------------
# CONFIG (SANITIZED)
# --------------------------------------------------------------------------------------------

ruta_carpeta = r"\\FILESERVER\Shared\RPA\dashboard_screenshots\output"

x_plus = 0      # Recortar desde el borde izquierdo
x_minus = 390   # Recortar desde el borde derecho
y_plus = 85     # Recortar desde el borde superior
y_minus = 310   # Recortar desde el borde inferior (ajustar según necesidad)

# Lista de rutas completas a excluir (placeholders)
rutas_excluidas = [
    # r"\\FILESERVER\Shared\RPA\dashboard_screenshots\output\no_procesar.png",
]

procesar_carpeta(ruta_carpeta, x_plus, x_minus, y_plus, y_minus, rutas_excluidas)
