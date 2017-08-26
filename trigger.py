#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Интерфейс для обработки событий
"""

import codecs
import os
import re
import smtplib
import sys
from datetime import datetime

from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText

from logger.logger import Logger

CP1251 = 'cp1251'
YEAR_MONTH_DAYS_ORDER = '%Y-%m-%d'
FLAG_READ_FILE = 'r'


class SMTPError(Exception):
    """ Ошибка SMTP """
    pass


class Trigger(object):
    """
    Класс интерфейс для обработки событий

    Если событие правда, то должно приходить сообшение
    """
    DESC = 'DESC'
    ACS = 'ASC'
    ORDERING_TYPES = [ACS, DESC]
    log = Logger(u"{message:<50s}")
    error_handle = Logger.ERROR
    warning_handler = Logger.WARNING
    info_handler = Logger.INFO

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
        self.pre_event_check()
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
            trigger_type,
            name,
            message_title,
            message_body,
            from_address,
            to_address,
            smtp_host,
            smtp_port,
            password,
            **kwargs
    ):
        self.trigger_type = trigger_type
        self.name = name
        self.message_title = message_title
        self.message_body = message_body
        self.from_address = from_address
        self.to_address = to_address
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.password = password
        self.message_container = MIMEMultipart()

    def pre_event_check(self):
        """ Проверка подключения """
        try:
            self.smtp_port = int(self.smtp_port)
        except (ValueError, AttributeError):
            message = (
                u"Ошибка номера порта. Порт "
                u"{} задан не верно.".format(
                    self.smtp_port
                )
            )
            self.log.row_message(level=self.error_handle, message=message)
            sys.stdout.write(message)
            raise SMTPError

        try:
            self.SERVER = smtplib.SMTP(self.smtp_host, int(self.smtp_port))
        except Exception as Error:
            message = u"Не удалось подключиться к серверу "
            sys.stdout.write(message)
            sys.stdout.write(Error.message)
            self.log.row_message(level=self.error_handle, message=message)
            self.log.row_message(
                level=self.error_handle, message=Error.message)
            raise SMTPError

        try:
            self.SERVER.starttls()
        except Exception as Error:
            message = u"Сервер не подддерживает метод "
            sys.stdout.write(message)
            sys.stdout.write(Error.message)
            self.log.row_message(level=self.error_handle, message=message)
            raise SMTPError

        try:
            self.SERVER.login(self.from_address, self.password)
        except Exception as Error:
            message = u"Неверный логин или пароль"
            sys.stdout.write(message)
            sys.stdout.write(Error.message)
            self.log.row_message(level=self.error_handle, message=message)
            self.log.row_message(
                level=self.error_handle, message=Error.message)
            raise SMTPError

    def run(self):
        super(BaseTriggerEvent, self).run()

    def send_mail(self):

        self.message_container[self.FROM] = self.from_address
        self.message_container[self.TO] = self.to_address
        self.message_container[self.SUBJECT] = self.message_title
        self.message_container.attach(
            MIMEText(
                self.message_body,
                self.CONTENT_TYPE_PLAIN,
                self.ENCODING)
        )

        self.SERVER.sendmail(
            self.from_address,
            self.to_address,
            self.message_container.as_string()
        )
        self.SERVER.quit()

class GTEDateModifyTrigger(BaseTriggerEvent):
    """ Триггер по дате изменения

        Если есть конкретный файл,
        который переодически должен изменяться. Например SQL бекап.
        вводим имя файла , путь и критичное количество дней
    """
    def __init__(self, path, file_name, older_days, **kwargs):
        try:
            self.older_days = int(older_days)
        except ValueError:
            self.older_days = 1
            self.log.row_message(
                level=self.warning_handler,
                message=u"Колчество дней задано не верно"
            )
            self.log.row_message(
                level=self.warning_handler,
                message=u"Колчество дней изменено на 1 день"
            )

        self.path = path
        self.file_name = file_name
        super(GTEDateModifyTrigger, self).__init__(**kwargs)

    def event(self):
        """
        Отправка сообщения если дата изменний больше, чем older_days
        """
        full_path = os.path.join(self.path, self.file_name )
        if not os.path.exists(full_path):
            self.log.row_message(
                level=self.warning_handler,
                message=u"Файл не найден"
            )
            return

        date_modify = datetime.fromtimestamp(
            os.path.getmtime(full_path)
        ).strftime('%Y-%m-%d')

        return (
            datetime.now() - datetime.strptime(
                date_modify, YEAR_MONTH_DAYS_ORDER)
        ).days >= self.older_days


class FileNotExistsTrigger(BaseTriggerEvent):
    """
    Триггер сущесвутет ли файл
    """
    def __init__(self, path, file_name, **kwargs):
        self.path = path
        self.file_name = file_name
        super(FileNotExistsTrigger, self).__init__(**kwargs)

    def event(self):
        """
        Отправка сообщения если файла нет
        """

        return not os.path.exists(
            os.path.join(
                self.path,
                self.file_name
            )
        )


class FileExistsTrigger(FileNotExistsTrigger):
    def event(self):
        """
        Отправка сообщения если файла есть
        """
        return os.path.exists(
            os.path.join(
                self.path,
                self.file_name
            )
        )


class RegularExpressionFolderOrFileNotExits(BaseTriggerEvent):
    """ Каталог(Или Файл) с маской не существет """
    def __init__(self, path, mask, **kwargs):
        self.path = path
        self.mask = mask
        super(RegularExpressionFolderOrFileNotExits, self).__init__(**kwargs)

    def event(self):
        """
        Отправка сообщения если каталога нет
        """
        return not any(
            re.match(self.mask, folder, re.UNICODE)
            for folder in os.listdir(self.path)
        )


class RegularExpressionFolderOrFileExits(
        RegularExpressionFolderOrFileNotExits):
    """ Каталог с маской существет """

    def event(self):
        """
        Отправка сообщения если каталог есть
        """
        return any(
            re.match(self.mask, folder, re.UNICODE)
            for folder in os.listdir(self.path)
        )


class AllWaysTrueTrigger(BaseTriggerEvent):
    """
    События запуска программы
    """
    def event(self):
        return True


class AllCopiesGTEOlderTriggerOrNotExists(BaseTriggerEvent):
    """
    Триггер для файлов создающихся автоматически

    Проверяют все файлы по маске, если среди них
    все файлы старше n - Дней , то отправляют сообщение.

    Если файла не найдено , так же срабатывает триггер
    """
    def __init__(self, mask, older_days, path, **kwargs):
        self.mask = mask
        self.path = path
        try:
            self.older_days = int(older_days)
        except ValueError:
            self.older_days = 1
            self.log.row_message(
                level=self.warning_handler,
                message=u"Колчество дней задано не верно"
            )
            self.log.row_message(
                level=self.warning_handler,
                message=u"Колчество дней изменено на 1 день"
            )

        super(
            AllCopiesGTEOlderTriggerOrNotExists, self).__init__(**kwargs)

    def event(self):
        diff_all_files = []
        for folder in os.listdir(self.path):
            item = re.match(self.mask, folder, re.UNICODE)
            if item:
                name_file = item.group(0)
                full_path = os.path.join(self.path, name_file)
                
                str_time = datetime.fromtimestamp(
                    os.path.getmtime(full_path)).strftime(
                    YEAR_MONTH_DAYS_ORDER)
                days_diff = (
                    datetime.now() - datetime.strptime(str_time,
                                                       YEAR_MONTH_DAYS_ORDER)
                ).days

                self.log.row_message(
                    level=self.info_handler,
                    message=u"Файлу:{} Дней:{}".format(name_file, days_diff)
                )
                diff_all_files.append(days_diff)
        if all(diff >= self.older_days for diff in diff_all_files):
            return True
        return False


class FirstFileLogOrderByDayItemFoundTrigger(BaseTriggerEvent):
    """
    Поиск текста в файле лога

    Проверяет самый новый (старый) файл лога,
    ищет в нем соотвествие строки mask_item
    """

    def __init__(
            self,
            path,
            file_log_mask,
            mask_item,
            encoding='utf-16',
            order=BaseTriggerEvent.ACS,
            **kwargs
    ):
        self.file_log_mask = file_log_mask
        self.mask_item = mask_item
        self.order = order
        self.encoding = encoding
        self.path = path

        super(
            FirstFileLogOrderByDayItemFoundTrigger, self).__init__(**kwargs)

    def additional_condition(self, **kwargs):
        return self.search_text_by_patter(**kwargs)

    def search_text_by_patter(self, first_file):
        self.log.row_message(
            level=self.info_handler,
            message=u"Поиск вырожения в файле {}".format(first_file)
        )
        with codecs.open(
                os.path.join(
                    self.path,
                    first_file,
                ),
                FLAG_READ_FILE,
                self.encoding) as file_log:
            for item in iter(file_log.readlines()):
                found_text = re.match(
                    self.mask_item, item, re.UNICODE)
                if found_text:
                    return True
        return

    def event(self):
        if self.order not in self.ORDERING_TYPES:
            message = (
                u"Не задан тип очередности (ASC, DESC)"
            )
            self.log.row_message(
                level=self.warning_handler,
                message=message
            )
            sys.stdout.write(message+'\r\n')
            return
        if self.order == self.DESC:
            self.order = True
        if self.order == self.ACS:
            self.order = False

        # Фильтр файлов по маске
        filtered_list = filter(
            lambda name: re.match(
                self.file_log_mask,
                name,
                re.UNICODE
            ),
            os.listdir(self.path)
        )

        # Сортировка файлов по времени модификации
        sorted_list = sorted(
            filtered_list,
            key=lambda name: datetime.fromtimestamp(
                os.path.getmtime(os.path.join(self.path, name))),
            reverse=self.order
        )

        if len(sorted_list):
            # Если в файле сущестует строка то срабатывает триггер
            first_file = sorted_list[0]
            return self.additional_condition(first_file=first_file)
        return


class FirstFileLogOrderByDayItemNotFoundTrigger(
    FirstFileLogOrderByDayItemFoundTrigger
):
    """
    Не найдена искомая сторока в файле
    """

    def search_text_by_patter(self, first_file):
        self.log.row_message(
            level=self.info_handler,
            message=u"Поиск вырожения в файле {}".format(first_file)
        )
        with codecs.open(
                os.path.join(
                    self.path,
                    first_file,
                ),
                FLAG_READ_FILE,
                self.encoding) as file_log:
            for item in iter(file_log.readlines()):
                found_text = re.match(
                    self.mask_item, item, re.UNICODE)

                if found_text:
                    return
        return True


class LTEBaitInFirstDayOrderedFileTrigger(
        FirstFileLogOrderByDayItemFoundTrigger):
    """
    Класс ищет последний(первый) файл, в каталоге
    с количеством Меньше или равно n - байт

    Для некоторых копий заведомо известно, что они не могут меньше
    чем n - байт. Если меньше , то отправлять сообщение
    """
    def __init__(
            self,
            path,
            file_log_mask,
            lte_baits=0,

            # Оставил для совместимости
            # order = 'DESC',
            mask_item='',
            **kwargs
    ):
        super(LTEBaitInFirstDayOrderedFileTrigger, self).__init__(
            path,
            file_log_mask,
            mask_item,
            **kwargs
        )
        self.lte_baits = lte_baits

    def check_bait_len(self, first_file):
        # TODO сделать обвертку для сообщений
        self.log.row_message(
            level=self.info_handler,
            message=u"Поиск вырожения в файле {}".format(first_file)
        )

        return os.stat(
            os.path.join(self.path, first_file)
        ).st_size <= int(self.lte_baits)

    def additional_condition(self, **kwargs):
        return self.check_bait_len(**kwargs)