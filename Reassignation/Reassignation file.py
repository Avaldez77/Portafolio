import poplib
import email
from email.utils import parsedate_to_datetime
from datetime import datetime, timedelta
import os
import re

# === RUTAS ===
base_path = r"\\103.20.120\80 - Stock Assignation"
excel = os.path.join(base_path, "Assignation")
mail = os.path.join(base_path, "Assignationmail")
os.makedirs(excel, exist_ok=True)
os.makedirs(mail, exist_ok=True)

# === POP3 ===

ruta_archivo = r"\\103.20.120\Share_Foldersclave.txt"
with open(ruta_archivo, encoding='utf-8') as archivo:
  contenido = archivo.read()
valor = contenido.strip()  
server = "pop3.w2.net"
username = "g@mail.com"
password = valor


# === Funciones auxiliares ===
def rgx(nombre):
    if not nombre:
        return None
    nombre = re.sub(r'[\n\r\t]', ' ', nombre)
    nombre = re.sub(r'[<>:"/\\|?*]', '_', nombre)
    nombre = re.sub(r'\s+', ' ', nombre)
    return nombre.strip()

def fechabusqueda():
    ahora = datetime.now()
    # Si es antes de las 5 PM → usa la fecha de hoy
    if ahora.hour < 17:
        return ahora.month, ahora.day
    else:
        # Si es después de las 5 PM → usa regla de fechas existente
        return regladefechas()

def regladefechas():
    hoy = datetime.today()
    weekday = hoy.weekday()
    if weekday <= 3:
        fecha = hoy + timedelta(days=1)
    else:
        diasfaltantes = (7 - weekday) % 7
        fecha = hoy + timedelta(days=diasfaltantes)
    # Devolvemos mes y día sin cero inicial obligatorio
    return fecha.month, fecha.day

def fechacorreo(email_message):
    try:
        fecha_str = email_message.get("Date")
        if fecha_str:
            return parsedate_to_datetime(fecha_str)
    except:
        pass
    return datetime.now()

def adjunto(part, carpeta_destino):
    filename = part.get_filename()
    if filename and filename.endswith(".xlsb"):
        filename_limpio = rgx(filename)
        if not filename_limpio:
            return False
        ruta_adjunto = os.path.join(carpeta_destino, filename_limpio)
        try:
            with open(ruta_adjunto, "wb") as f:
                f.write(part.get_payload(decode=True))
            return True
        except Exception as e:
            print(f"Error al guardar adjunto {filename}: {str(e)}")
            return False
    return False

def correoyfile(pop_conn, msg_id):
    try:
        response, lines, _ = pop_conn.retr(msg_id)
        raw_email = b"\n".join(lines)
        email_message = email.message_from_bytes(raw_email)
        fecha_correo = fechacorreo(email_message)
        timestamp = fecha_correo.strftime("%Y%m%d_%H%M%S")
        nombre_archivo_eml = f"Correo_{msg_id}_{timestamp}.eml"
        ruta_correo = os.path.join(mail, nombre_archivo_eml)
        with open(ruta_correo, "wb") as f:
            f.write(raw_email)
        for part in email_message.walk():
            if part.get_content_maintype() == "multipart":
                continue
            if part.get("Content-Disposition") is None:
                continue
            adjunto(part, excel)
    except Exception as e:
        print(f"Error procesando correo {msg_id}: {str(e)}")

# === MAIN ===
def main():
    mes, dia = fechabusqueda()
    print(f"Buscando correos para el día: {mes}/{dia}")
   
    try:
        pop_conn = poplib.POP3_SSL(server, 995)
        pop_conn.user(username)
        pop_conn.pass_(password)
       
        num_messages = len(pop_conn.list()[1])
        print(f"Total de correos en buzón: {num_messages}")
    
        inicio = max(1, num_messages - 60 + 1)
        rangos = range(inicio, num_messages + 1)
        masreciente = []
        asunto_regex = re.compile(rf"GPC-PA\s*Assignation\s*0*{mes}/0*{dia}", re.IGNORECASE)

        for i in reversed(rangos):
            response, msg_lines, _ = pop_conn.top(i, 0)
            email_message = email.message_from_bytes(b"\n".join(msg_lines))
            subject = email_message.get("Subject", "")

            if asunto_regex.search(subject):
                fecha = fechacorreo(email_message)
                masreciente.append((i, fecha))

        masreciente.sort(key=lambda x: x[1], reverse=True)
        if masreciente:
            msg_id, fecha = masreciente[0]
            print(f"Procesando el correo más reciente (ID: {msg_id}, Fecha: {fecha})")
            correoyfile(pop_conn, msg_id)
        else:
            print("No se encontraron correos con el asunto especificado")
           
    except Exception as e:
        print(f"Error general: {str(e)}")
    finally:
        pop_conn.quit()
        print("Proceso completado")

if __name__ == "__main__":
    main()