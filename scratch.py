import os
import imaplib
import email
from email.header import decode_header
from dotenv import load_dotenv
load_dotenv()


mail = imaplib.IMAP4_SSL("imap.gmail.com")
mail.login(os.environ.get("GMAIL_ADDRESS"), os.environ.get("GMAIL_APP_PASSWORD"))
mail.select("inbox")

status, messages = mail.search(None, "UNSEEN")
print(f"Status: {status}, unread message count: {len(messages[0].split())}")
message_ids= messages[0].split()

if (not(len(message_ids) == 0)):
    lastest_id= message_ids[-1]

    status, message_text= mail.fetch(lastest_id, "(RFC822)")

    raw_text= message_text[0][1]

    msg= email.message_from_bytes(raw_text)
    subject, encoding = decode_header(msg["Subject"])[0]
    if isinstance(subject, bytes):
        subject = subject.decode(encoding or "utf-8")

    sender= msg.get("From")

    body= None
    if msg.is_multipart():
        for part in msg.walk():
            content_type= part.get_content_type()
            content_disposition = str(part.get("Content-Disposition"))
            if content_type == "text/plain" and "attachment" not in content_disposition:
                body = part.get_payload(decode=True).decode(errors="replace")
                break
    else:
        body = msg.get_payload(decode=True).decode(errors="replace")

else:
    print("No unread messages found")


mail.logout()