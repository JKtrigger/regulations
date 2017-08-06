#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Интерфейс для обработки событий
"""
import sys
import smtplib
import os
import re
from email import encoders
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEBase import MIMEBase
from datetime import datetime


class Trigger(object):
    """
    Класс интерфейс для обработки событий

    Если событие правда, то должно приходить сообшение
    """
    def event(self):
        """ проверка события """
        raise NotImplemented

    def send_mail(self):
        """ отправка сообщения """
        raise NotImplemented

    def pre_event_check(self):
        """ пред проверка события """
        raise NotImplemented

    def run(self):
        if self.pre_event_check():
            return
        if not self.event():
            return
        self.send_mail()


class BaseTriggerEvent(Trigger):
    """ Базовый класс для событий """

    SERVER = ""
    FROM = 'From'
    TO = 'To'
    SUBJECT = 'Subject'
    ENCODING = 'utf-8'
    CONTENT_TYPE_PLAIN = 'plain'
    CONTENT_TYPE_APPLICATION = 'application'
    SUB_TYPE_CONTENT_TYPE_OCTET_STREAM = 'octet-stream'
    PRESENTATION_INFORMATION_CONTENT_DISPOSITION = 'Content-Disposition'

    def __init__(
            self,
            message_title,
            message_body,
            from_address,
            to_address,
            SMTP_host,
            SMTP_port,
            password
    ):
        self.message_title = message_title
        self.message_body = message_body
        self.from_address = from_address
        self.to_address = to_address
        self.SMTP_host = SMTP_host
        self.SMTP_port = SMTP_port
        self.password = password
        self.MESSAGE_CONTAINER = MIMEMultipart()

    def pre_event_check(self):
        """ Проверка подключения """
        try:
            self.SERVER = smtplib.SMTP(self.SMTP_host, self.SMTP_port)

        except Exception as Error:
            sys.stdout.write("Server cannot initialised smtp connection\n")
            sys.stdout.write(Error.message)
            return True

        try:
            self.SERVER.starttls()
        except Exception as Error:
            sys.stdout.write("Server does not support methods")
            sys.stdout.write(Error.message)
            return True

        try:
            self.SERVER.login(self.from_address, self.password)
        except Exception as Error:
            sys.stdout.write("Login or password incorrect")
            sys.stdout.write(Error.message)
            return True

    def run(self):
        super(BaseTriggerEvent, self).run()

    def send_mail(self):
        self.MESSAGE_CONTAINER[self.FROM] = self.from_address
        self.MESSAGE_CONTAINER[self.TO] = self.to_address
        self.MESSAGE_CONTAINER[self.SUBJECT] = self.message_title
        self.MESSAGE_CONTAINER.attach(
            MIMEText(
                self.message_body,
                self.CONTENT_TYPE_PLAIN,
                self.ENCODING)
        )

        self.SERVER.sendmail(
            self.from_address,
            self.to_address,
            self.MESSAGE_CONTAINER.as_string()
        )
        self.SERVER.quit()

    def add_attach_email(self, path_filename):
        """ добавление вложения  """
        attachment = open(path_filename, 'rb')
        message_attach = MIMEBase(
            self.CONTENT_TYPE_APPLICATION,
            self.SUB_TYPE_CONTENT_TYPE_OCTET_STREAM
        )
        message_attach.set_payload(attachment.read())
        encoders.encode_base64(message_attach)
        message_attach.add_header(
            self.PRESENTATION_INFORMATION_CONTENT_DISPOSITION,
            'attachment; filename= {}'.format(path_filename)
        )
        self.MESSAGE_CONTAINER.attach(message_attach)


class GTEDateModifyTrigger(BaseTriggerEvent):
    """ Триггер по дате изменения """
    def __init__(self, path_file_name, date_modify, older_days, **kwargs):
        self.date_modify = date_modify
        self.older_days = older_days
        self.path_file_name = path_file_name
        super(GTEDateModifyTrigger, self).__init__(**kwargs)

    def event(self):
        """
        Отправка сообщения если дата изменний больше, чем older_days
        """
        return (
            datetime.now() - datetime.strptime(self.date_modify, "%Y-%m-%d")
        ).days > self.older_days

    def run(self):
        super(GTEDateModifyTrigger, self).run()


class FileNotExistsTrigger(BaseTriggerEvent):
    """
    Триггер сущесвутет ли файл
    """
    def __init__(self, path_file_name, **kwargs):
        self.path_file_name = path_file_name
        super(FileNotExistsTrigger, self).__init__(**kwargs)

    def event(self):
        """
        Отправка сообщения если файла нет
        """
        return not os.path.exists(self.path_file_name)

    def run(self):
        super(FileNotExistsTrigger, self).run()


class FileExistsTrigger(FileNotExistsTrigger):
    def event(self):
        """
        Отправка сообщения если файла есть
        """
        return os.path.exists(self.path_file_name)


class RegularExpressionFolderNotExits(BaseTriggerEvent):
    """ Каталог с маской не существет """
    def __init__(self, path, mask, **kwargs):
        self.path = path
        self.mask = mask
        super(RegularExpressionFolderNotExits, self).__init__(**kwargs)

    def event(self):
        """
        Отправка сообщения если каталога нет
        """
        return not any(
            re.match(self.mask, folder)
            for folder in os.listdir(self.path)
        )

    def run(self):
        super(RegularExpressionFolderNotExits, self).run()


class RegularExpressionFolderExits(RegularExpressionFolderNotExits):
    """ Каталог с маской существет """

    def event(self):
        """
        Отправка сообщения если каталог есть
        """
        return any(
            re.match(self.mask, folder)
            for folder in os.listdir(self.path)
        )


class RegularExpressionFileNotExits(RegularExpressionFolderNotExits):
    """ Файла не существует """
    pass


class RegularExpressionFileExits(RegularExpressionFolderExits):
    """ Файл существует """
    pass


class AllWaysTrueTrigger(BaseTriggerEvent):
    """ События запуска программы
    """
    def event(self):
        return True


class AllCopiesGTEOlderTriggerOrNotExists(BaseTriggerEvent):
    """
    Тригер для файлов создающихся автоматически

    Проверяют все файлы по маске, если среди них
    все файлы старше n - Дней , то отправляют сообщение.

    Если фала не найдено , так же срабатывает триггер
    """

    def __init__(self, path, mask, older_days, **kwargs):
        self.path = path
        self.mask = mask
        self.older_days = older_days
        super(
            AllCopiesGTEOlderTriggerOrNotExists, self).__init__(**kwargs)

    def event(self):
        diff_all_files = []
        for folder in os.listdir(self.path):
            item = re.match(self.mask, folder)

            if item:
                name_file = item.group(0)
                full_path = os.path.join(self.path, name_file)

                str_time = datetime.fromtimestamp(
                    os.path.getmtime(full_path)).strftime('%Y-%m-%d')
                days_diff = (
                    datetime.now() - datetime.strptime(str_time, "%Y-%m-%d")
                ).days
                diff_all_files.append(days_diff)

        if all(diff > self.older_days for diff in diff_all_files):
            return True

        return False
