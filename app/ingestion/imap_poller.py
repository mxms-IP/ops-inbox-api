import os
import imaplib
import email
from email.header import decode_header
from dotenv import load_dotenv
from app.models.schema import TicketIn
load_dotenv()



def fetch_unread_emails() -> list[TicketIn]:
    """
    Connect, select inbox, search UNSEEN.
    For each unread message: parse sender/subject/body (reuse the
    logic from your scratch script), construct a TicketIn, mark
    the message as Seen (so it isn't re-processed next poll — hint:
    mail.store(msg_id, '+FLAGS', '\\Seen')), and collect into a list.
    Return the list of TicketIn objects. If there are zero unread
    messages, return an empty list — don't error.
    """

    tickets=[]

    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(os.environ.get("GMAIL_ADDRESS"),os.environ.get("GMAIL_APP_PASSWORD"))
    mail.select("inbox")

    status,message_list= mail.search(None,"UNSEEN")
    print(f"Status: {status}, unread message count: {len(message_list[0].split())}")
    message_ids=message_list[0].split()
    
    for id in message_ids:
        status, raw_text= mail.fetch(id, "(RFC822)")
        message_text= email.message_from_bytes(raw_text[0][1])

        sender= message_text.get("From")

        subject, encoding = decode_header(message_text["Subject"])[0]
        if isinstance(subject, bytes):
            subject= subject.decode(encoding or "utf-8")

        body= None
        if message_text.is_multipart():
            for part in message_text.walk():
                content_type= part.get_content_type()
                content_disposition= str(part.get_content_disposition())
                if content_type == "text/plain" and "attachment" not in content_disposition:
                    body = part.get_payload(decode=True).decode(errors="replace")
                    break


        else:
            body=part.get_payload(decode=True).decode(errors="replace")


        try:
            ticket=TicketIn(
                sender=sender,
                subject=subject,
                body=body
                
            )

            tickets.append(ticket)
        except Exception as e:
            print(f"There was an error parsing this email. Please try again {e}" )

        

    mail.logout()
        
    return tickets