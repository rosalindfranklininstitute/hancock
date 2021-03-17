import smtplib, ssl
from hancock import app

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
    def send_email(cls,  to_address, message):

            server = cls.connect_to_smtp()
            print(app.config['SMTP_SENDER_EMAIL'])
            server.sendmail(from_addr=app.config['SMTP_SENDER_EMAIL'], to_addrs=to_address, msg=message)


