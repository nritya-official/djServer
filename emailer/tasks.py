import os
from celery import Celery
import logging
from utils.common_utils import is_valid_entity_type, COLLECTIONS, NOTIFICATION
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from jinja2 import Environment, FileSystemLoader, Template
from utils.flags import get_celery_broker_url
from utils.env_loader import base_web_url

logging.basicConfig(level=logging.INFO)
#logger = logging.getLogger(__name__)
logger = logging.getLogger("Celery")

CELERY_BROKER_URL = get_celery_broker_url()

app = Celery('tasks', broker=CELERY_BROKER_URL)

app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)


def generate_tbus(email_data):
    title = None
    body = None
    url = None
    subject = None
    base_url = base_web_url()

    collection_name = email_data.get('collection_name', None)
    operation_type = email_data.get('operation_type', NOTIFICATION.OP_CREATE)
    entity_id = email_data.get('entity_id', None)
    entity_name = None
    city = None 
    email_metadata = email_data.get('metadata',None)

    if email_metadata :
        entity_name = email_metadata.get('entity_name',None)

    if operation_type == NOTIFICATION.OP_CREATE:
        if collection_name == COLLECTIONS.USER:
            subject = f'Welcome to Nritya !'
            title = f'Successful Sign Up! Welcome to Nritya!'
            body = f'Welcome to Nritya! You can explore studio, workshops, courses and classes in your city.'
            url = f'{base_url}/#/profile'
            return title, body, url, subject

        subject = f'New {collection_name} {operation_type} : {entity_name} !'
        title = f'{collection_name} {operation_type} successfully'
        body = f'You have successfully added your {collection_name}: {entity_name}.'

        if collection_name == COLLECTIONS.STUDIO:
            subject = f'New {collection_name} Studio : {entity_name} !'
            body = body + "You can now add related workshop, courses, openclasses and gain visibility."
            url = f"{base_url}/#/studio/{entity_id}"
        elif collection_name == COLLECTIONS.WORKSHOPS:
            subject = f'New {collection_name} Workshop : {entity_name} !'
            url = f"{base_url}/#/workshop/{entity_id}"
        elif collection_name == COLLECTIONS.COURSES:
            subject = f'New {collection_name} Course : {entity_name} !'
            url = f"{base_url}/#/course/{entity_id}"
        elif collection_name == COLLECTIONS.OPENCLASSES:
            subject = f'New {collection_name} open class : {entity_name} !'
            url = f"{base_url}/#/openClass/{entity_id}"
        elif collection_name == COLLECTIONS.USER_KYC:
            subject = f'Your Profile Verification Details Have Been Successfully Submitted !'
            url = f"{base_url}/#/profile"
    
    elif operation_type == NOTIFICATION.OP_KYC_REJECTED:
        subject = f'Profile Verification Update !'
        url = f"{base_url}/#/profile"
    
    elif operation_type == NOTIFICATION.OP_KYC_APPROVED:
        subject = f'Your Profile Has Been Successfully Verified !'
        url = f"{base_url}/#/profile"

    return title, body, url, subject

def load_html_template(title, body, url):
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__)) 
        template_dir = os.path.join(current_dir, 'templates')
        logger.info(f"Loading templates from directory: {template_dir}")
        logger.info(f"title : {title},body: {body},url: {url}")
        env = Environment(loader=FileSystemLoader(template_dir))
        template = env.get_template('new-email.html')
        html_content = template.render(title=title, body=body, url=url )
        return html_content
    except Exception as e:
        raise Exception(f"Error loading template: {str(e)}")

def send_gmail_email(receiver_email, title, body, url, subject ):
    # Set up the server
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    sender_email = "nritya.contact@gmail.com"
    app_password = "mnqorvtscfghukqu"

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    html_content = load_html_template(title, body, url)
    logger.info(f'title {title}, body {body}, url {url}, subject {subject}')
    msg.attach(MIMEText(html_content, 'html'))

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls() 
        server.login(sender_email, app_password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        logger.info(f'Email sent successfully from {sender_email} to {receiver_email}')

    except Exception as e:
        logger.info(f'Failed to send email. Error: {str(e)}')

    finally:
        server.quit()

def send_outlook_email(receiver_email, title, body, url, subject ):
    # Set up the server
    smtp_server = "smtp.office365.com"
    smtp_port = 587
    sender_email = "nritya@nritya.co.in"
    app_password = "W9CGFFRp3Ygsv/y"

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    html_content = load_html_template(title, body, url)
    logger.info(f'title {title}, body {body}, url {url}, subject {subject}')
    msg.attach(MIMEText(html_content, 'html'))

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls() 
        server.login(sender_email, app_password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        logger.info(f'Email sent successfully from {sender_email} to {receiver_email}')

    except Exception as e:
        logger.info(f'Failed to send email. Error: {str(e)}')

    finally:
        server.quit()

def load_html_template_adv(title, body, url, subject, operation_type, collection_name, entity_id, metadata):
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__)) 
        template_dir = os.path.join(current_dir, 'templates')
        logger.debug(f"Loading templates from directory: {template_dir}")
        logger.info(f"title : {title},metadata: {metadata},url: {url}, operation_type{operation_type}")
        env = Environment(loader=FileSystemLoader(template_dir))
        html_content = None
        if operation_type == NOTIFICATION.OP_CREATE:
            if collection_name == COLLECTIONS.USER:
                template = env.get_template('SignUp.html')
                html_content = template.render(url=url )

            elif collection_name == COLLECTIONS.STUDIO:
                template = env.get_template('AddStudio.html')
                html_content = template.render(
                    url=url,
                    studio_name=metadata.get('studio_name'),
                    studio_id=metadata.get('studio_id'),
                    studio_street_name=metadata.get('studio_street_name'),
                    studio_city_name=metadata.get('studio_city_name')
                )
            elif collection_name == COLLECTIONS.WORKSHOPS:
                template = env.get_template('AddWorkshop.html')
                html_content = template.render(
                    url=url,
                    entity_name=metadata.get('entity_name'),
                    entity_id=metadata.get('entity_id'),
                    studio_name=metadata.get('studio_name'),
                    studio_id=metadata.get('studio_id'),
                    studio_street_name=metadata.get('studio_street_name'),
                    studio_city_name=metadata.get('studio_city_name')
                )

            elif collection_name == COLLECTIONS.OPENCLASSES:
                template = env.get_template('AddOpenClass.html')
                html_content = template.render(
                    url=url,
                    entity_name=metadata.get('entity_name'),
                    entity_id=metadata.get('entity_id'),
                    studio_name=metadata.get('studio_name'),
                    studio_id=metadata.get('studio_id'),
                    studio_street_name=metadata.get('studio_street_name'),
                    studio_city_name=metadata.get('studio_city_name')
                )

            elif collection_name == COLLECTIONS.COURSES:
                template = env.get_template('AddCourse.html')
                html_content = template.render(
                    url=url,
                    entity_name=metadata.get('entity_name'),
                    entity_id=metadata.get('entity_id'),
                    studio_name=metadata.get('studio_name'),
                    studio_id=metadata.get('studio_id'),
                    studio_street_name=metadata.get('studio_street_name'),
                    studio_city_name=metadata.get('studio_city_name')
                )
            elif collection_name == COLLECTIONS.USER_KYC:
                template = env.get_template('Kyc.html')
                html_content = template.render(
                    url=url,
                )
        
        elif operation_type == NOTIFICATION.OP_KYC_REJECTED:
            template = env.get_template('Kyc_Failed.html')
            html_content = template.render(
                url=url,
            )
        
        elif operation_type == NOTIFICATION.OP_KYC_APPROVED:
            template = env.get_template('Kyc_Approved.html')
            html_content = template.render(
                url=url,
            )

        return html_content
    except Exception as e:
        raise Exception(f"Error loading template: {str(e)}")

def send_outlook_email_adv(receiver_email, title, body, url, subject, operation_type, collection_name, entity_id, metadata):
    # Set up the server
    smtp_server = "smtp.office365.com"
    smtp_port = 587
    sender_email = "nritya@nritya.co.in"
    app_password = "W9CGFFRp3Ygsv/y"

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    html_content = load_html_template_adv(title, body, url, subject, operation_type, collection_name, entity_id, metadata)
    logger.info(f'title {title}, body {body}, url {url}, subject {subject}')
    msg.attach(MIMEText(html_content, 'html'))

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls() 
        server.login(sender_email, app_password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        logger.info(f'Email sent successfully from {sender_email} to {receiver_email}')

    except Exception as e:
        logger.info(f'Failed to send email. Error: {str(e)}')

    finally:
        server.quit()

def send_outlook_email(receiver_email, title, body, url, subject ):
    # Set up the server
    smtp_server = "smtp.office365.com"
    smtp_port = 587
    sender_email = "nritya@nritya.co.in"
    app_password = "W9CGFFRp3Ygsv/y"

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    html_content = load_html_template(title, body, url)
    logger.info(f'title {title}, body {body}, url {url}, subject {subject}')
    msg.attach(MIMEText(html_content, 'html'))

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls() 
        server.login(sender_email, app_password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        logger.info(f'Email sent successfully from {sender_email} to {receiver_email}')

    except Exception as e:
        logger.info(f'Failed to send email. Error: {str(e)}')

    finally:
        server.quit()


@app.task(name='tasks.process_email_task')
def process_email_task(email_data):
    try:
        process_type = email_data.get('type',None)
        if process_type == NOTIFICATION.TYPE_CRUD:
            logger.info(f"Processing email to: {email_data['emails']}, collection_name: {email_data['collection_name']}, operation_type: {email_data['operation_type']}, entity_id: {email_data['entity_id']},  metadata: {email_data['metadata']}")
            receiver_email = email_data.get('emails', None)
            collection_name = email_data.get('collection_name', None)
            operation_type = email_data.get('operation_type', NOTIFICATION.OP_CREATE)
            entity_id = email_data.get('entity_id', None)
            metadata = email_data.get('metadata', None)

            if operation_type in [NOTIFICATION.OP_KYC_APPROVED, NOTIFICATION.OP_KYC_REJECTED]:
                collection_name = email_data.get(COLLECTIONS.USER_KYC, None)
                if receiver_email:
                    title, body, url, subject = generate_tbus(email_data)
                    send_outlook_email_adv(receiver_email, title, body, url, subject, operation_type, collection_name, entity_id, metadata)


            if receiver_email and collection_name and entity_id and metadata:
                title, body, url, subject = generate_tbus(email_data)
                send_outlook_email_adv(receiver_email, title, body, url, subject, operation_type, collection_name, entity_id, metadata)

            #title, body, url, subject = generate_tbus(email_data)
            #send_outlook_email(receiver_email, title, body, url, subject )

    except Exception as e:
        logger.error(f"Failed to process email task: {str(e)}")
        logger.debug(f"Email data: {email_data}")

if __name__ == "__main__":
    logger.info("Starting Celery worker...")
    app.worker_main(['worker', '--loglevel=info'])
