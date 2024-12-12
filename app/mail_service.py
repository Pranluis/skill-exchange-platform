import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
import random


sender_email = os.getenv('EMAIL_USER')
sender_password = os.getenv('EMAIL_PASS')


used_otps = set()

def generate_unique_otp():
    """Generate a unique 6-digit OTP."""
    while True:
        otp = random.randint(1000, 9999)  # Generate a 6-digit number
        if otp not in used_otps:
            used_otps.add(otp)
            return otp



def send_welcome_mail(recmail, recname):
    recipient_email = recmail
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = "Welcome to Skillup"
    html_body = (
            """
            <!DOCTYPE html>
<html>
<head>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f6f9fc;
            margin: 0;
            padding: 0;
        }
        .email-container {
            max-width: 600px;
            margin: 20px auto;
            background-color: #ffffff;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            overflow: hidden;
        }
        .email-header {
            background-color: #4CAF50;
            color: #ffffff;
            text-align: center;
            padding: 20px;
        }
        .email-header h1 {
            margin: 0;
            font-size: 24px;
        }
        .email-body {
            padding: 20px;
            line-height: 1.6;
        }
        .email-body h2 {
            font-size: 20px;
            color: #333333;
        }
        .email-body p {
            font-size: 16px;
            color: #555555;
            margin: 10px 0;
        }
        .email-footer {
            text-align: center;
            padding: 20px;
            background-color: #f1f1f1;
            font-size: 14px;
            color: #888888;
        }
        .btn {
            display: inline-block;
            padding: 10px 20px;
            margin: 20px 0;
            background-color: #4CAF50;
            color: #ffffff;
            text-decoration: none;
            border-radius: 5px;
        }
        .btn:hover {
            background-color: #45a049;
        }
    </style>
</head>
<body>
    <div class="email-container">
        <div class="email-header">
            <h1>Welcome to SkillUp</h1>
        </div>
        <div class="email-body">
            <h2>Hello User_Name,</h2>
            <p>
                Thank you for joining SkillUp! We're excited to have you onboard. 
                Our platform offers amazing tools and resources to help you achieve your goals.
            </p>
            <p>
                To get started, click the button below and explore the possibilities:
            </p>
            <a href="https://skillup-skill-exchange-platform.onrender.com" class="btn">Get Started</a>
            <p>
                If you have any questions, feel free to reach out to our support team. 
                We're here to help!
            </p>
            <p>
                Cheers,<br>
                The SkillUp Team
            </p>
        </div>
        <div class="email-footer">
             2024 SkillUp. All rights reserved.
        </div>
    </div>
</body>
</html>


            """
        )
    html_body = html_body.replace("User_Name", recname)
    # body = body.replace("XXX", jobname)
    msg.attach(MIMEText(html_body, 'html', 'utf-8'))
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


