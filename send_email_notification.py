# from dotenv import load_dotenv, find_dotenv
# import os
# import smtplib
# from email.mime.multipart import MIMEMultipart
# from email.mime.text import MIMEText
# from datetime import datetime

# # Load environment variables from .env file
# dotenv_path = find_dotenv()
# if dotenv_path:
#     load_dotenv(dotenv_path)
# else:
#     raise FileNotFoundError("No .env file found! Make sure it's in the same directory.")

# def send_email(receiver_email, subject, body):
#     sender_email = os.getenv('EMAIL')  # Fetch sender email
#     sender_password = os.getenv('EMAIL_APP_PASSWORD')  # Fetch app password

#     if not sender_email or not sender_password:
#         raise ValueError("Email or password not set in environment variables.")

#     # Create the email
#     msg = MIMEMultipart()
#     msg['From'] = sender_email
#     msg['To'] = receiver_email
#     msg['Subject'] = subject
#     msg.attach(MIMEText(body, 'plain'))

#     try:
#         # Connect to the email server and send the email
#         mail = smtplib.SMTP('smtp.gmail.com', 587)
#         mail.ehlo()
#         mail.starttls()
#         mail.login(sender_email, sender_password)
#         mail.sendmail(sender_email, receiver_email, msg.as_string())
#         mail.close()

#         print(f"Email sent successfully to {receiver_email}!")
#     except smtplib.SMTPAuthenticationError:
#         print('Authentication failed. Check your email credentials.')
#     except smtplib.SMTPException as e:
#         print(f'Failed to send email. Error: {e}')


# # Notify registration
# def notify_registration(name, email, password):
#     # Receiver's email
#     receiver_email = "shaiksameerhussain2104@gmail.com"  # Replace with your desired recipient email

#     # Subject of the email
#     subject = "New User Registration Alert"

#     # Registration time
#     registration_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

#     # Body of the email
#     body = f"""
#     A new user has registered on your platform: https://project-document-creator.onrender.com

#     User Details:
#     Name: {name}
#     Email: {email}
#     Password: {password}
#     Registration Time: {registration_time}

#     Do check this user's authenticity.

#     Check user details in the database:
#     https://console.firebase.google.com/project/project-document-creator/database/project-document-creator-default-rtdb/data
#     """

#     # Send the email
#     send_email(receiver_email, subject, body)

import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
from dotenv import load_dotenv

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

# Notify registration
def notify_registration(name, email, password):
    # Receiver's email
    receiver_email = "shaiksameerhussain2104@gmail.com"  # Replace with your desired recipient email

    # Subject of the email
    subject = "New User Registration Alert"

    # Registration time
    registration_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Body of the email
    body = f"""
    A new user has registered on your platform: https://project-document-creator.onrender.com

    User Details:
    Name: {name}
    Email: {email}
    Password: {password}
    Registration Time: {registration_time}

    Do check this user's authenticity.

    Check user details in the database:
    https://console.firebase.google.com/project/project-document-creator/database/project-document-creator-default-rtdb/data
    """

    # Send the email
    send_email(receiver_email, subject, body)
