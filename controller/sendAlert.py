__author__ = "Julio Luna"
__email__ = "jcluna@unicauca.edu.co"

from controller.base import BaseController
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from settings import config

class SendAlertFunction(BaseController):

    def sendEmail(self):
        mail_content = '''Hola,
        El presente correo es para informarle que el análisis de similitud ejecutado ha finalizado.    
        Para ver los resultados del mismo por favor ingrese a la plataforma con sus credenciales.
        Saludos.'''
        #The mail addresses and password
        sender_address = config['EMAIL_USERNAME']
        sender_pass = config['EMAIL_PASS']
        receiver_address = config['EMAIL_ADDRESS']
        #Setup the MIME
        message = MIMEMultipart()
        message['From'] = sender_address
        message['To'] = receiver_address
        message['Subject'] = 'El proceso de análisis de similitud a terminado.'   #The subject line
        #The body and the attachments for the mail
        message.attach(MIMEText(mail_content, 'plain'))
        #Create SMTP session for sending the mail
        session = smtplib.SMTP('smtp.gmail.com', 587) #use gmail with port
        session.starttls() #enable security
        session.login(sender_address, sender_pass) #login with mail_id and password
        text = message.as_string()
        session.sendmail(sender_address, receiver_address, text)
        session.quit()
