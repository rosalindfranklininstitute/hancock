import smtplib, ssl
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
            app.logger.debug(f"unable to connect:{e}")
            return None
        return server

    @classmethod
    def send_email(cls,  to_address, main_body, url_string_io):
        message = create_email(to_address, main_body, url_string_io)
        server = cls.connect_to_smtp()
        server.sendmail(from_addr=app.config['SMTP_SENDER_EMAIL'], to_addrs=to_address, msg=message)


def create_email(to_address, main_body_file=None,  attachment_bytes=None):
    subject = "Batch Data Retrieve Job"
    default_message ="This message is sent from hancock. If you have received this in error please ignore"
    if not main_body_file:
        main_body = default_message
    else:
        try:
            with open(main_body_file) as f:
                main_body = f.read()
        except Exception as e:
            app.logger(e)
            app.logger.info("Main body message could not be read defaulting to simple message")
            main_body = default_message


    # Create a multipart message and set headers
    message = MIMEMultipart()
    message["From"] = app.config['SMTP_SENDER_EMAIL']
    message["To"] = to_address
    message["Subject"] = subject

    # Add body to email
    message.attach(MIMEText(main_body, "plain"))

    # Add file as application/octet-stream
    # Email client can usually download this automatically as attachment
    if attachment_bytes:
        try:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment_bytes)
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
        except Exception as e:
            app.logger.debug(e)
            app.logger.info('could not make attachment')
            main_body ="Email attachment failed on creation. Please contact the RFI AI team."
            message.attach(MIMEText(main_body, "plain"))

    else:
        app.logger.info('no attachment specified')
    return message.as_string()



