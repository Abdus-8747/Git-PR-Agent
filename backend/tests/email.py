import smtplib

ADMIN_EMAIL_ADDRESS = "admin@gmail.com"
ADMIN_EMAIL_PASS = "Rshabhedbjh27"

def send_email(email: str):
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(ADMIN_EMAIL_ADDRESS, ADMIN_EMAIL_PASS)
        server.sendmail(ADMIN_EMAIL_ADDRESS, email, "Hello")
    print("Email sent")

send_email("user1@gmail.com")