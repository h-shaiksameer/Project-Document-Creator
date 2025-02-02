import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
from dotenv import load_dotenv
import requests 
import logging

logging.basicConfig(level=logging.INFO)


load_dotenv()
# Check for environment variables directly (for Render)
sender_email = os.getenv('EMAIL')
sender_password = os.getenv('EMAIL_APP_PASSWORD')

if not sender_email or not sender_password:
    raise ValueError("Email or password not set in environment variables. Ensure they are configured correctly.")

def send_email(receiver_email, subject, body):
    # Create the email
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        # Connect to the email server and send the email
        mail = smtplib.SMTP('smtp.gmail.com', 587)
        mail.ehlo()
        mail.starttls()
        mail.login(sender_email, sender_password)
        mail.sendmail(sender_email, receiver_email, msg.as_string())
        mail.close()

        print(f"Email sent successfully to {receiver_email}!")
    except smtplib.SMTPAuthenticationError:
        print('Authentication failed. Check your email credentials.')
    except smtplib.SMTPException as e:
        print(f'Failed to send email. Error: {e}')





send_email("9121sameer@gmail.com","HI","Hello")