import smtplib , ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

class Mail():
    from_addr = ''
    to_addr = ''
    msg_body = ''
    msg_subject = ''

    @staticmethod
    def Send_Mail(mail_info):
      msg = MIMEMultipart()
      msg['From'] = mail_info.from_addr
      msg['To'] = mail_info.to_addr
      msg['Subject'] = mail_info.msg_subject
      body = mail_info.msg_body
      msg.attach(MIMEText(body, 'plain'))
      server = smtplib.SMTP('mail.pishgaman.net', 25)
      server.login("oss-problems@pishgaman.net", "Oss_9r0@123")
      text = msg.as_string()
      server.sendmail(mail_info.from_addr, mail_info.to_addr, text)

      return 'class method called', mail_info



class Ticket():
    Queue = ''
    Requestor = ''
    Subject = ''
    Cc = ''
    AdminCc = ''
    Owner = ''
    Status = ''
    Priority = ''
    InitialPriority = ''
    FinalPriority = ''
    TimeEstimated = ''
    Starts = ''
    Due = ''
    Text = ''

