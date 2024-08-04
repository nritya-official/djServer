import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from .flags import *
import json

def load_templates(template_path='emailer/email_templates.json'):
    with open(template_path, 'r') as file:
        templates = json.load(file)
    return templates

def render_template(template_name, variables, templates):
    template = templates.get(template_name)
    if not template:
        raise ValueError(f"No template found for {template_name}")
    
    subject = template['subject']
    body = template['body']

    for key, value in variables.items():
        placeholder = f"{{{{{key}}}}}"
        subject = subject.replace(placeholder, value)
        body = body.replace(placeholder, value)

    return subject, body

def send_email_passkey(receiver_emails, subject, body, sender_email=None,email_provider=None):
    if(email_provider == "outlook" or email_provider is None or sender_email is None ):
        smtp_server = OUTLOOK_SMTP_SERVER
        passkey = OUTLOOK_PASSKEY
        sender_email = "ayushraj763@outlook.com"
    elif(email_provider == "gmail"):
        smtp_server = GMAIL_SMTP_SERVER
        passkey = GMAIL_PASSKEY

    try:
        msg = MIMEMultipart()
        msg['From'] = sender_email
        if isinstance(receiver_emails, list):
            msg['To'] = ', '.join(receiver_emails)
        else:
            msg['To'] = receiver_emails
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        with smtplib.SMTP(smtp_server, SMTP_PORT) as server:
            server.starttls() 
            server.login(sender_email, passkey)
            server.sendmail(sender_email, receiver_emails, msg.as_string())
            print(f"Email successfully sent to {receiver_emails}")

    except Exception as e:
        print(f"Failed to send email. Error: {str(e)}")
