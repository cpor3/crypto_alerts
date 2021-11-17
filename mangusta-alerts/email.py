import smtplib, ssl
import os

GMAIL_ADDRESS = os.environ.get('GMAIL_ADDRESS')
GMAIL_PASSWORD = os.environ.get('GMAIL_PASSWORD')

def send_email(to_addr: str, message: str):
    print('Creando SSL...', end='')
    context = ssl.create_default_context()
    print('Ok')

    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as gmail_server:
        gmail_server.login(GMAIL_ADDRESS, GMAIL_PASSWORD)
        gmail_server.sendmail(GMAIL_ADDRESS, to_addr, message)
