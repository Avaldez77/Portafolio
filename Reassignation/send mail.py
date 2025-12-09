import urllib3
from email.message import EmailMessage
from email.headerregistry import Address
from email.utils import make_msgid
import sys
from io import StringIO
import pandas as pd
import smtplib, ssl
context = ssl.create_default_context()
urllib3.disable_warnings()   


# EMAIL MODULE --------------------------------------------------------------------------------------------
ruta_archivo = r"\\103.20.120\01_RPAs\clave\clave.txt"
with open(ruta_archivo, encoding='utf-8') as archivo:
  contenido = archivo.read()
valor = contenido.strip()  
port = 25  # For SSL
username="g"
password = valor

file_paths = [
    r"C:\Users\g\Desktop\RPA\Reasgination-\mat.txt",
    r"C:\Users\g\Desktop\RPA\Reasgination-\so.txt"]
file_contents = {}
for file_path in file_paths:
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
        # Codificar el contenido en utf-8 y guardarlo en el diccionario con el nombre correspondiente
        if "mat.txt" in file_path:
            file_contents["mat"] = content.encode('utf-8')
        elif "so.txt" in file_path:
            file_contents["so"] = content.encode('utf-8')
print('NEW EMAIL MODULE --------------------------------------------------------------------------------------------')

msg = EmailMessage()
msg['Subject'] = "Reasgination Validation RPA"
from_addr = "g@mail.com"
to_addrs = ["a.chacon@mail.com"]

msg["From"] = from_addr

msg["To"] =to_addrs

msg.set_content(f"""
Subject: Reasgination process Finalized
Process finalzied running
----------------------------------------------------------------
Attached 2 files
----------------------------------------------------------------""")
msg.add_alternative(f"""\
<html>
  <head></head>
  <body>
    <p>Reasgination process Finalized:
    </p><br>
    ----------------------------------------------------------------
    <br> 2 files attached
    ---------------------------------------------------------------
    <br><br>
g                
  </body>
</html>
""",subtype='html')
msg.add_attachment(file_contents["mat"], maintype='text', subtype='txt', filename="mat.txt")
msg.add_attachment(file_contents["so"], maintype='text', subtype='txt', filename="so.txt")

try:
    s = smtplib.SMTP('smtp.w2.mail.net', 25)
    s.login(username, password)
    print("Sending email")
    s.sendmail(from_addr, to_addrs, bytes(msg))
    # s.sendmail(bytes(msg))
    # s.send_message(msg)
    print("EMAIL SENT SUCCESSFULLY!")
    s.quit()
except smtplib.SMTPException:
    print( "Error:"), sys.exc_info()[0]
    # /EMAIL MODULE -------------------------------------------------------------------------------------------