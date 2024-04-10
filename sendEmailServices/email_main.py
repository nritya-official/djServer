from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from email.mime.application import MIMEApplication
import smtplib
import time
from .convert import generate_ticket_pdf
from io import BytesIO
from .flags import FLAGS

def generate_message(studioOwner=False, studioName="", customerName="", className=""):
    timestamp_ist = time.strftime('%Y-%m-%d %H:%M:%S IST', time.localtime())

    if studioOwner:
        subject = "New Booking Notification"
        body = (f"Dear {studioName} Studio Owner,\n\n"
                f"We have received a new booking from {customerName} for the class '{className}'.\n"
                f"The booking details are as follows:\n"
                f"Customer: {customerName}\n"
                f"Class: {className}\n"
                f"Booked at Timestamp (IST): {timestamp_ist} .\n Customer can avail within {FLAGS.EXPIRES_WITHIN_DAYS} days.\n\n"
                f"Thank you,\n"
                f"Nritya")
    else:
        subject = "Booking Confirmation"
        body = (f"Dear {customerName},\n\n"
                f"Thank you for booking the class '{className}' at {studioName} Studio.\n"
                f"The details of your booking are as follows:\n"
                f"Studio: {studioName}\n"
                f"Class: {className}\n"
                f"Booked at Timestamp (IST): {timestamp_ist} You can avail within {FLAGS.EXPIRES_WITHIN_DAYS} days.\n"
                f"Please arrive on time and enjoy your class!\n\n"
                f"Thank you,\n"
                f"Nritya")

    return subject, body, timestamp_ist

def send_emails_stc(studioName, customerName, className, customerEmail, studioEmail,address="ABC Street",studio_timing="7pm-8pm",studio_days="M,W,F"):
    qr_code_link= 'https://www.youtube.com/watch?v=by_Z8AofRnE'
    s = smtplib.SMTP('smtp.gmail.com', FLAGS.PORT)
    s.starttls()
    s.login(FLAGS.SENDEREMAIL, FLAGS.PASSKEY)

    # Generate messages for studio owner and customer
    subject_studio, body_studio, timestamp_s = generate_message(studioOwner=True, studioName=studioName, customerName=customerName, className=className)
    subject_customer, body_customer, timestamp_c = generate_message(studioOwner=False, studioName=studioName, customerName=customerName, className=className)

    # Create a PDF ticket for the customer
    pdf_ticket_buffer = generate_ticket_pdf(customerName, studioName, className,address, qr_code_link,timestamp_c,studio_timing,studio_days)
    # Create a multipart message for studio owner
    msg_studio = MIMEMultipart()
    msg_studio['From'] = FLAGS.SENDEREMAIL
    msg_studio['To'] = studioEmail
    msg_studio['Subject'] = subject_studio
    msg_studio.attach(MIMEText(body_studio, 'plain'))

    # Create a multipart message for customer
    msg_customer = MIMEMultipart()
    msg_customer['From'] = FLAGS.SENDEREMAIL
    msg_customer['To'] = customerEmail
    msg_customer['Subject'] = subject_customer
    msg_customer.attach(MIMEText(body_customer, 'plain'))

    # Attach the PDF to the customer's email
    payload = MIMEBase('application', 'octate-stream', Name='ticket.pdf')
    payload.set_payload(pdf_ticket_buffer.read())
    encoders.encode_base64(payload)
    payload.add_header('Content-Disposition', 'attachment', filename='ticket.pdf')
    msg_customer.attach(payload)

    # Send emails
    s.sendmail(FLAGS.SENDEREMAIL, studioEmail, msg_studio.as_string())
    s.sendmail(FLAGS.SENDEREMAIL, customerEmail, msg_customer.as_string())

    s.quit()

send_emails_stc("Hello Default Try 3", "Ayush Raj", "Salsa 4 u", "rayushbpgc@gmail.com", "radarshbpgc@gmail.com",'ABC Street, Gurugram',"6pm-7pm","M,W,F")

'''
- free_trial_bookings (collection)
  - {booking_id} (document)
    - studio_uid: "123456" 
    - studio_name: "ABC Studio"
    - studio_address: "ABC Street,Delhi"
    - user_uid: "789012" 
    - user_name: "Ayush Raj" 
    - class_uuid: "abcdef" 
    - class_name: "Salsa 4 U" 
    - class_timing: "7pm-8pm" 
    - class_days: "M W F" 
    - booking_date: Timestamp
'''
