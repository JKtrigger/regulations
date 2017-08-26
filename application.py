#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    Запуск приложения
"""
import os
import sys

from config_API import ConfigAPI
from helpers import InfoLog, WarningLog, ErrorLog, get_class


class ApplicationError(Exception):
    pass


class Application(object):
    """
    Запуск приложения

    Чтение настроек из файла настроек
    и последовательный запуск заданий.
    """
    os_variable = 'config_file'
    info_log = InfoLog()
    warning_log = WarningLog()
    info_log.row_message(message=u"Запуск приложения")
    try:
        file_name = os.environ[os_variable]
    except KeyError:
        message = u"Не задана системная переменная {}".format(os_variable)
        warning_log.row_message(
            message=message)
        warning_log.row_message(
            message=u"Задайте системню переменню с помощью команды")
        warning_log.row_message(
            message=u"setx.exe config_file 'path - to - file'  /M")

        sys.stdout.write(message + u"\n")
        sys.stdout.write(u"Переменная должна "
                         u"сожержать в себе полный путь до файла \n "
                         u"и имя файла")

        sys.stdout.write(u"Поиск в папке проекта " + u"\n")
        file_name = "mail_sender.conf"

    info_log.row_message(message=u"Чтение файла конфигурации")
    conf = ConfigAPI(file_name)
    conf.read_config()
    info_log.row_message(message=u"Файл конфигурации успешно загружен")

    for task in iter(conf.tasks):
        message = u"{} Задание получено".format(task.name)
        sys.stdout.write(message+u"\n")
        info_log.row_message(message=message)
        event_type = get_class(task.trigger_type)
        try:
            Event = event_type(**task.options)

        except TypeError:
            warning_log.row_message(message=u"Задание пропущено")
            warning_log.row_message(
                message=u"Наследование экспортов ограничено одним потомком"
            )
            message = u"{} Задание пропущено".format(task.name)
            sys.stdout.write(message+u"\n")
            info_log.row_message(message=message)

        else:
            Event.run()
            message = u"{} Задание выполнено".format(task.name)
            sys.stdout.write(message+u"\n")
            info_log.row_message(message=message)


if __name__ == "__main__":
    u""" Запуск приложения """
    Application_instance = Application()

