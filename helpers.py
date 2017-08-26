#!/usr/bin/env python
# -*- coding: utf-8 -*-

from logger.logger import Logger
from trigger import (
    GTEDateModifyTrigger, AllCopiesGTEOlderTriggerOrNotExists,
    FileNotExistsTrigger, FileExistsTrigger,
    RegularExpressionFolderOrFileNotExits, RegularExpressionFolderOrFileExits,
    AllWaysTrueTrigger, FirstFileLogOrderByDayItemFoundTrigger,
    FirstFileLogOrderByDayItemNotFoundTrigger,
    LTEBaitInFirstDayOrderedFileTrigger
)


class ApplicationError(Exception):
    """ Ошибка приложения """
    __module__ = 'exceptions'


class ConfigApiError(ApplicationError):
    pass


class ErrorLog(Logger):
    """ Лог уровня ERROR """
    format_message = u"{message: <50}"
    level = Logger.ERROR

    def __init__(self, format_message=format_message):
        super(ErrorLog, self).__init__(format_message)

    def row_message(self, level=level, **kwargs):
        super(ErrorLog, self).row_message(level=self.level, **kwargs)


class WarningLog(ErrorLog):
    """ Лог уровня WARNING """
    level = Logger.WARNING


class InfoLog(ErrorLog):
    """ Лог уровня INFO """
    level = Logger.INFO


def get_class(class_name):
    """
    Функция хелпер. Возвращает класс по имени класса

    :param class_name: строка имя класса
    :return: инстанс класса
    """
    triggers = [
        GTEDateModifyTrigger, AllCopiesGTEOlderTriggerOrNotExists,
        FileNotExistsTrigger, FileExistsTrigger,
        RegularExpressionFolderOrFileNotExits,
        RegularExpressionFolderOrFileExits,
        AllWaysTrueTrigger, FirstFileLogOrderByDayItemFoundTrigger,
        FirstFileLogOrderByDayItemNotFoundTrigger,
        LTEBaitInFirstDayOrderedFileTrigger
    ]
    trigger_names = map(lambda x: x.__name__, triggers)

    if class_name in trigger_names:
        return globals()[class_name]
