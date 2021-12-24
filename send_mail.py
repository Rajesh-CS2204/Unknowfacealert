import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime import multipart
from email import encoders
import os
import stat


def rmtree(top):
    for root, dirs, files in os.walk(top, topdown=False):
        for name in files:
            filename = os.path.join(root, name)
            os.chmod(filename, stat.S_IWUSR)
            os.remove(filename)
        for name in dirs:
            os.rmdir(os.path.join(root, name))
    os.rmdir(top)


def send_mail(unknown_list):
    print('[INFO] Preparing Mail...')
    from_address = 'whitedevil2204@gmail.com'
    to_address = 'lavanyalava221199@gmail.com'
    mail = MIMEMultipart()
    mail['From'] = from_address
    mail['To'] = to_address
    mail['Subject'] = 'Unauthorized Person Found'
    mail_body = ''
    mail.attach(MIMEText(mail_body, 'plain'))
    for attach_file in unknown_list:
        attachment = open(attach_file, "rb")
        p = multipart.MIMEBase('application', 'octet-stream')
        p.set_payload(attachment.read())
        encoders.encode_base64(p)
        p.add_header('Content-Disposition', "attachment; filename= %s" % attach_file.split('/')[-1])
        mail.attach(p)
    s = smtplib.SMTP('smtp.gmail.com', 587)
    print('[INFO] Creating SMTP Server...')
    s.starttls()
    s.login(from_address, '@Varalakshmi222')
    text = mail.as_string()
    print('[INFO] Sending Mail...')
    s.sendmail(from_address, to_address, text)
    print('[INFO] Mail Sent...')
    s.quit()
    print('[INFO] Closing SMTP Server...')
    os.system('rmdir /S /Q "{}"'.format('.tmp'))
