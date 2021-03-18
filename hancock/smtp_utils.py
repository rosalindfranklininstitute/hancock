import smtplib, ssl,email
from hancock import app


from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

class SMTPConnect:
    @classmethod
    def connect_to_smtp(cls):
        context = ssl.create_default_context()


        # Try to log in to server and send email
        #TODO: generalize this so we can make different security connections
        try:
            server = smtplib.SMTP(app.config['SMTP_SERVER'], app.config['SMTP_PORT'])
            server.ehlo()  # Can be omitted
            server.starttls(context=context)  # Secure the connection
            server.ehlo()  # Can be omitted
            server.login(app.config['SMTP_LOGIN_USER'], app.config['SMTP_LOGIN_PASSWORD'])
        except Exception as e:
            print(f"unable to connect:{e}")

        return server

    @classmethod

    def send_email(cls,  to_address, url_string_io):
        message =create_email(to_address, url_string_io)
        server = cls.connect_to_smtp()
        print(app.config['SMTP_SENDER_EMAIL'])
        server.sendmail(from_addr=app.config['SMTP_SENDER_EMAIL'], to_addrs=to_address, msg=message)


def create_email( to_address, url_bytes_io):
    subject = "Batch Data Retrieve Job"
    body = "Please find attached links to your data. - sent from hancock"


    # Create a multipart message and set headers
    message = MIMEMultipart()
    message["From"] = app.config['SMTP_SENDER_EMAIL']
    message["To"] = to_address
    message["Subject"] = subject

    # Add body to email
    message.attach(MIMEText(body, "plain"))



    # Add file as application/octet-stream
    # Email client can usually download this automatically as attachment
    part = MIMEBase("application", "octet-stream")
    part.set_payload(url_bytes_io)
    filename = f"{datetime.strftime(datetime.now(), format='%Y%m%d_%H%M')}_data_url.txt"

    # Encode file in ASCII characters to send by email
    encoders.encode_base64(part)

    # Add header as key/value pair to attachment part
    part.add_header(
        "Content-Disposition",
        f"attachment; filename= {filename}",
    )

    # Add attachment to message and convert message to string
    message.attach(part)
    return message.as_string()


