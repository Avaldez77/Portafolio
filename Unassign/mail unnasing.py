
# %%
import os
import time
from datetime import datetime
from pathlib import Path

# --------------------------------------------------------------------------------------
# RUTAS (PLACEHOLDERS - CAMBIA A TU ENTORNO)
# --------------------------------------------------------------------------------------
file_path_to_attach = r"C:\RPA\Desallocate\Excels\desallocation.xlsx"  # Adjuntar
so_file_path = r"C:\RPA\Desallocate\Excels\SO.xlsx"                    # Hora

# Obtener la hora de creación del archivo SO.xlsx
file_info = os.stat(so_file_path)
creation_time = file_info.st_ctime

# Convertir la hora de creación a formato legible y a datetime
formatted_creation_time = time.ctime(creation_time)
creation_datetime = datetime.fromtimestamp(creation_time)

# Obtener la hora actual
current_datetime = datetime.now()

# Calcular la diferencia de tiempo
time_difference = current_datetime - creation_datetime

print(f"La hora de creación del archivo SO.xlsx es: {formatted_creation_time}")
print(f"La diferencia de tiempo es: {time_difference}")

# --------------------------------------------------------------------------------------
# EMAIL MODULE (SANITIZED)
# --------------------------------------------------------------------------------------
from email.message import EmailMessage
import smtplib
import ssl

print("NEW EMAIL MODULE --------------------------------------------------------------------------------------------")

# --- SMTP CONFIG (PLACEHOLDERS - CAMBIA A TU ENTORNO) ---
SMTP_HOST = "smtp.example.com"
SMTP_PORT = 587  # típico con STARTTLS (cámbialo si tu infra usa 25/465)
SMTP_USERNAME = "svc.rpa"  # usuario genérico (placeholder)

# Contraseña: usa variable de entorno (RECOMENDADO)
# En Windows (PowerShell):  setx SMTP_PASSWORD "TU_PASSWORD"
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

# Alternativa: archivo local genérico (NO red/NO nombres reales)
# secret_file = r"C:\RPA\secrets\smtp_password.txt"
# with open(secret_file, encoding="utf-8") as f:
#     SMTP_PASSWORD = f.read().strip()

if not SMTP_PASSWORD:
    raise RuntimeError("No se encontró SMTP_PASSWORD en variables de entorno (o en el archivo de secretos).")

# --- EMAIL ADDRESSES (PLACEHOLDERS) ---
from_addr = "rpa-bot@example.com"
to_addrs = [
    "ops-team@example.com",
    "process-owner@example.com",
    "it-support@example.com",
]

msg = EmailMessage()
msg["Subject"] = "Deallocation Validation RPA"
msg["From"] = from_addr
msg["To"] = ", ".join(to_addrs)

# Cuerpo del correo en HTML
html_body = f"""
<html>
  <head></head>
  <body>
    <p>Reallocation process finalized.</p>
    <p>Time finalized: {current_datetime.strftime("%Y-%m-%d %H:%M:%S")}</p>
    <p>File creation time (SO.xlsx): {formatted_creation_time}</p>
    <p>Process time: {time_difference}</p>
    <hr>
  </body>
</html>
"""

# (opcional) texto plano + HTML
msg.set_content(
    "Reallocation process finalized.\n"
    f"Time finalized: {current_datetime.strftime('%Y-%m-%d %H:%M:%S')}\n"
    f"File creation time (SO.xlsx): {formatted_creation_time}\n"
    f"Process time: {time_difference}\n"
)
msg.add_alternative(html_body, subtype="html")

# Adjuntar el archivo desallocation.xlsx
with open(file_path_to_attach, "rb") as file:
    file_content = file.read()
    file_name = Path(file_path_to_attach).name
    msg.add_attachment(
        file_content,
        maintype="application",
        subtype="vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=file_name,
    )

try:
    context = ssl.create_default_context()
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as s:
        s.ehlo()
        s.starttls(context=context)  # si tu server NO usa TLS, elimina esto y ajusta puerto
        s.ehlo()
        s.login(SMTP_USERNAME, SMTP_PASSWORD)
        print("Sending email...")
        s.sendmail(from_addr, to_addrs, msg.as_string())
        print("EMAIL SENT SUCCESSFULLY!")
except smtplib.SMTPException as e:
    print(f"Error: {e}")
