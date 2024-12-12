import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
import os
import random


sender_email = os.getenv('EMAIL_USER')
sender_password = os.getenv('EMAIL_PASS')


used_otps = set()

def generate_unique_otp():
    """Generate a unique 6-digit OTP."""
    while True:
        otp = random.randint(100000, 999999)  # Generate a 6-digit number
        if otp not in used_otps:
            used_otps.add(otp)
            return otp



def send_welcome_mail(recmail):
    recipient_email = recmail
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = "Welcome to Skillup"
    body = (
            f"Hi there,\n\n"
            f"Welcome to SkillUp! We are thrilled to have you onboard.\n"
            f"Explore the features, connect with mentors, and grow your skills.\n\n"
            f"Start your journey here: https://skillup-skill-exchange-platform.onrender.com\n\n"
            f"Cheers,\nSkillUp Team"
        )
    # body = body.replace("Applicant", recname)
    # body = body.replace("XXX", jobname)
    msg.attach(MIMEText(body, 'plain'))
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(sender_email, sender_password)
    text = msg.as_string()
    server.sendmail(sender_email, recipient_email, text)
    server.quit()
    print("Email sent successfully!")


def send_confirmation_mail(recmail, generated_otp):
    recipient_email = recmail
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = "Confirmation Mail with a Verification link"
    body = (
            f"Hi there,\n\n"
            f"Thank you for signing up for [Your Platform Name]. Please confirm your email address by providing your OTP sent on your provided email address:\n"
            f"{generated_otp}\n\n"
            f"If you did not create this account, you can safely ignore this email.\n\n"
            f"Cheers,\nSkillUp Team"
        )
    # body = body.replace("Applicant", recname)
    # body = body.replace("XXX", jobname)
    msg.attach(MIMEText(body, 'plain'))
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(sender_email, sender_password)
    text = msg.as_string()
    server.sendmail(sender_email, recipient_email, text)
    server.quit()
    print("Email sent successfully!")


