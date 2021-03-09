import smtplib, ssl
from hancock import app

class SMTPConnect:
    @classmethod
    def connect_to_smpt(cls):
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
    def send_email(cls, from_address, to_address, message):
        try:
            server = cls.connect_to_smpt()
            server.sendmail(from_address, to_address, message)
        except Exception as e:
            print(f'unable to send: {e}')

