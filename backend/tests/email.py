import smtplib
import os
from dotenv import load_dotenv

load_dotenv()

ADMIN_EMAIL_ADDRESS = os.getenv("ADMIN_EMAIL_ADDRESS")
ADMIN_EMAIL_PASS = os.getenv("ADMIN_EMAIL_PASS")

def send_email(email: str):
    with smtplib.SMTP(ADMIN_EMAIL_ADDRESS, 587) as server:
        server.starttls()
        server.login(ADMIN_EMAIL_ADDRESS, ADMIN_EMAIL_PASS)
        server.sendmail(ADMIN_EMAIL_ADDRESS, email, "Hello from Admin! Your request has been processed successfully.")
    print("Email sent")

send_email("user1@gmail.com")