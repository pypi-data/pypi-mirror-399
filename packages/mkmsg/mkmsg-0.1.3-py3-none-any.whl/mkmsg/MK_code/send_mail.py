import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr
class Send_mail:
    def __init__(self, email_sender: str, app_password: str, your_name: str, subject: str, body: str, email_receiver: str):
        self.email_sender = email_sender
        self.app_password = app_password
        self.your_name = your_name
        self.subject = subject
        self.body = body
        self.email_receiver = email_receiver
        """
        Send a plain text email.

        Args:
            email_sender (str): sender's email address
            app_password (str): sender's email password or app password
            subject (str): email subject
            body (str): email body (plain text)
            email_receiver (str): recipient's email address
        """
        msg = MIMEText(body, "plain", "utf-8")
        msg['Subject'] = subject
        msg['From'] = formataddr((your_name, email_sender))
        msg['To'] = email_receiver
        
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as sender_email:
            sender_email.login(email_sender, app_password)
            sender_email.sendmail(email_sender, email_receiver, msg.as_string())