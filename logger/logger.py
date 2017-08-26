#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Журнал работы приложения """
import codecs
from datetime import datetime

import os


class Logger(object):
    """
    Класс журнала
    """
    INFO, WARNING, ERROR = range(0, 3)
    LOG_LEVEL = {
        WARNING: 'WAINING',
        INFO: 'INFO',
        ERROR: 'ERROR'
    }

    def __init__(self, format_message):
        self.format_message = format_message
        if not isinstance(self.format_message, basestring):
            raise TypeError(
                u"Assignment variable 'format_message' is not string")
        self.format_message = (
            u"{level:10s} {time:20s}" +
            format_message +
            u"\r\n"
        )

    def row_message(self, level=INFO, **kwargs):
        """ Запись в журнал """
        level = self.LOG_LEVEL.get(level, self.LOG_LEVEL[self.INFO])
        file_name = datetime.now().strftime('%Y-%m-%d') + '.txt'
        time = datetime.now().strftime('[%H:%M:%S]')
        with codecs.open(os.path.join('./logs', file_name), 'a', 'utf-8') as log_file:
            row = self.format_message.format(
                level=level,
                time=time,
                **kwargs
            )
            log_file.write(row)


if __name__ == "__main__":
    application = Logger(format_message=u" {message:50s}")
    application.row_message(message=u"Привет мир")
