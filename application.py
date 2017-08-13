#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    Запуск приложения
"""
import sys

from config_API import ConfigAPI
from trigger import (
    GTEDateModifyTrigger, AllCopiesGTEOlderTriggerOrNotExists,
    FileNotExistsTrigger, FileExistsTrigger,
    RegularExpressionFolderOrFileNotExits, RegularExpressionFolderOrFileExits,
    AllWaysTrueTrigger, FirstFileLogOrderByDayItemFoundTrigger,
    FirstFileLogOrderByDayItemNotFoundTrigger,
    LTEBaitInFirstDayOrderedFileTrigger
)


def get_class(class_name):
    """
    Функция хелпер. Возвращает класс по имени класса

    :param class_name: строка имя класса
    :return: инстанс класса
    """
    # TODO отдельный exception для не найденных
    found_class = globals()[class_name]
    if found_class in [
        GTEDateModifyTrigger, AllCopiesGTEOlderTriggerOrNotExists,
        FileNotExistsTrigger, FileExistsTrigger,
        RegularExpressionFolderOrFileNotExits,
        RegularExpressionFolderOrFileExits,
        AllWaysTrueTrigger, FirstFileLogOrderByDayItemFoundTrigger,
        FirstFileLogOrderByDayItemNotFoundTrigger,
        LTEBaitInFirstDayOrderedFileTrigger
    ]:
        return found_class


class Application(object):
    """
    Запуск приложения

    Чтение настроек из файла настроек
    и последовательный запуск заданий.
    """
    sys.stdout.write(u"start application \n")
    file_name = "mail_sender.conf"
    sys.stdout.write(u"initialisation conf \n")
    conf = ConfigAPI(file_name)
    sys.stdout.write(u"read conf\n")
    conf.read_config()

    for task in iter(conf.tasks):
        sys.stdout.write(u"{} running \n".format(task.name))
        event_type = get_class(task.trigger_type)
        Event = event_type(**task.options)
        Event.run()
        sys.stdout.write(u"{} done \n".format(task.name))


if __name__ == "__main__":
    u""" Запуск приложения """
    Application_instance = Application()

