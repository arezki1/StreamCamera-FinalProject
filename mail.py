def mailto():

    #import all necessary packages
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    from email.mime.base import MIMEBase
    from email import encoders
    from picamera import PiCamera
    import threading
    from time import sleep

    #define email credentials
    email_user = 'email'
    email_password = 'password'
    email_send = 'email to sent to'




        

    #start sending the email

    #defime the subject
    subject = 'subject'

    #defne the message body
    msg = MIMEMultipart()
    msg['From'] = email_user
    msg['To'] = email_send
    msg['Subject'] = subject

    body = 'A new event occured!'
    msg.attach(MIMEText(body,'plain'))

    #attaching the image file to the email body
    filename='image.jpg'

    #try to attach the file
    try:        
        attachment  =open(filename,'rb')
    except Exception as err:
        print('Image does not exist')
        print(err)
        

    part = MIMEBase('application','octet-stream')
    part.set_payload((attachment).read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition',"attachment; filename= "+filename)

    msg.attach(part)
    text = msg.as_string()

    try:
        
        server = smtplib.SMTP('smtp.gmail.com',587)
        server.starttls()
        server.login(email_user,email_password)

        server.sendmail(email_user,email_send,text)
        print("email sent out ..")
        
    except smtplib.SMTPConnectError:
        #showing a message
        print("Connection Failed")
        #closing the server in case of an error
        server.quit()
    except Exception as err:
        
        #showing a message
        print("Some other error that I wasn't expecting occurred")
        print(err)
        #closing the server in case of an error
        server.quit()
        
    server.quit()
mailto()           
