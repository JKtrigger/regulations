#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    Send report via mail
"""

import smtplib
from datetime import datetime
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEBase import MIMEBase
from email import encoders
from ConfigParser import ConfigParser

# -----------------------------------------------------------------------------
# Константы
# -----------------------------------------------------------------------------
FROM = 'From'
TO = 'To'
SUBJECT = 'Subject'
ENCODING = 'utf-8'
CONTENT_TYPE_PLAIN = 'plain'
content_type_application = 'application'
SUB_TYPE_CONTENT_TYPE_OCTET_STREAM = 'octet-stream'
PRESENTATION_INFORMATION_CONTENT_DISPOSITION = 'Content-Disposition'

# -----------------------------------------------------------------------------
# Инициализация
# -----------------------------------------------------------------------------
config = ConfigParser()
config.readfp(open('mail_sender.conf'))
from_address = config.get('mail settings', 'from_address')
to_address = config.get('mail settings', 'to_address')
SMTP_host = config.get('mail settings', 'SMTP_host')
SMTP_port = config.get('mail settings', 'SMTP_host')
password = config.get('mail settings', 'mkonji3029zxc')

# -----------------------------------------------------------------------------
# Тело пиьма
# -----------------------------------------------------------------------------

message_container = MIMEMultipart()
message_container[FROM] = from_address
message_container[TO] = to_address

message_container[SUBJECT] = u"Проверить Бекап Норк Палм"
body = u"Тестовое сообщение   {}".format(datetime.now())
message_container.attach(MIMEText(body, CONTENT_TYPE_PLAIN, ENCODING))

# -----------------------------------------------------------------------------
# Прикрепить файл
# -----------------------------------------------------------------------------

filename = 'send_post'
attachment = open('send_post.py', 'rb')
message_attach = MIMEBase(
    content_type_application,
    SUB_TYPE_CONTENT_TYPE_OCTET_STREAM
)
message_attach.set_payload(attachment.read())
encoders.encode_base64(message_attach)
message_attach.add_header(
    PRESENTATION_INFORMATION_CONTENT_DISPOSITION,
    'attachment; filename= {}'.format(filename)
)

message_container.attach(message_attach)

# -----------------------------------------------------------------------------
# Отправка письма
# -----------------------------------------------------------------------------

server = smtplib.SMTP(SMTP_host, SMTP_port)
server.starttls()
server.login(from_address, password)
text = message_container.as_string()
server.sendmail(from_address, to_address, text)
server.quit()
