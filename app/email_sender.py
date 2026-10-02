import os
import smtplib
from email.message import EmailMessage
import os
from dotenv import load_dotenv

load_dotenv()

def send_email(to: str, subject: str, body: str) -> None:
    """
    Build an EmailMessage with From = GMAIL_ADDRESS, To = `to`,
    Subject = f"Re: {subject}", content = `body`.
    Connect via smtplib.SMTP_SSL("smtp.gmail.com", 465), login with
    GMAIL_ADDRESS / GMAIL_APP_PASSWORD, send_message, quit.
    Let any exception propagate — same pattern as classify_llm and
    TicketIn construction: this function's job is to send or fail
    loudly, not decide what a failure means.
    """
    mail_response = EmailMessage()

    mail_response["From"] = os.environ.get("GMAIL_ADDRESS")
    mail_response["To"] = to
    mail_response["Subject"] = f"Re: {subject}"
    mail_response.set_content(body)

    mail = smtplib.SMTP_SSL("smtp.gmail.com")
    mail.login(os.environ.get("GMAIL_ADDRESS"),os.environ.get("GMAIL_APP_PASSWORD"))

    mail.send_message(mail_response)
    mail.quit()

    pass