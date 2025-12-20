import os
from pathlib import Path
import json
import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.base import MIMEBase
from email import encoders
from email.utils import make_msgid

# --------------------------------------------------------------------------------------------
# CONFIG SMTP (SANITIZED)
# --------------------------------------------------------------------------------------------
CREDENTIALS_FILE = r"\\FILESERVER\Shared\RPA\secrets\smtp_password.txt"

SMTP_HOST = "smtp.company.internal"
SMTP_PORT = 25
SMTP_USER = "service.account"
FROM_ADDR = "service.account@company.com"

# JSON con estructura:
# [
#   {"file_path": "\\\\FILESERVER\\Shared\\RPA\\reports\\img1.png", "emails": ["recipient1@company.com", "recipient2@company.com"]},
#   ...
# ]
RECIPIENTS_JSON = r"\\FILESERVER\Shared\RPA\mailing\recipients.json"

# --------------------------------------------------------------------------------------------
# EMAIL BODY (GENERIC)
# --------------------------------------------------------------------------------------------
BODY_HTML = """
<p>Hello,</p>
<p>Please find attached the weekly report image. It is also embedded inline in this email.</p>
"""

BODY_TEXT = (
    "Hello,\n\n"
    "Please find the weekly report image.\n"
    "It is shown in the email body and also attached as a PNG.\n\n"
    "Regards"
)


def load_password(path: str) -> str:
    try:
        with open(path, encoding="utf-8") as f:
            return f.read().strip()
    except FileNotFoundError:
        raise FileNotFoundError("Credentials file not found. Update CREDENTIALS_FILE.")


def enviar_correos():
    smtp_pass = load_password(CREDENTIALS_FILE)

    with open(RECIPIENTS_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as smtp:
        smtp.login(SMTP_USER, smtp_pass)

        for entry in data:
            file_path = entry.get("file_path", "")
            to_addrs = [e.strip() for e in entry.get("emails", []) if e and e.strip()]

            if not to_addrs:
                print(f"[WARN] No valid emails for file_path={file_path}. Skipping...")
                continue

            if not os.path.exists(file_path):
                print(f"[WARN] File not found: {file_path}. Skipping...")
                continue

            file_name = Path(file_path).name
            if Path(file_name).suffix.lower() != ".png":
                print(f"[WARN] Not a PNG: {file_name}. Skipping...")
                continue

            # Subject limpio, sin nombres internos
            subject_name_
