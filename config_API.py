#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    Инстанцирование задач из файла настроек
"""

import codecs
import os.path
from ConfigParser import ConfigParser

from helpers import ErrorLog, ConfigApiError
from trigger import FLAG_READ_FILE

UTF_WITH_BOM = 'utf-8-sig'


class ConfigAPI(object):
    """ Фабрика для инстанцирования триггеров
    """

    config_parser = ConfigParser()
    error_log = ErrorLog()
    ACTIVE_TASK = 'active_task'
    requirement_options = [ACTIVE_TASK]

    TRIGGER_TYPE = 'trigger_type'
    MESSAGE = 'message'
    GTE_DAYS = 'GTE_DAYS'

    export_key = 'export'

    tasks = []

    def __init__(self, file_name):
        self.file_name = file_name

    def check_file_config(self, *sections):
        """ Проверка обязательных секций  """
        return all(
            self.config_parser.has_section(section) for section in sections)

    def check_file_exists(self):
        """ Проверка существует ли файл """
        if not (os.path.isfile(self.file_name)):
            self.error_log.row_message(
                message=u"Не обнаружен Файл {}".format(self.file_name)
            )
            raise ConfigApiError

        self.config_parser.readfp(
            codecs.open(
                self.file_name,
                FLAG_READ_FILE,
                UTF_WITH_BOM)
        )

    def read_config(self):
        if self.check_file_exists():
            return
        if not self.check_file_config(*self.requirement_options):
            self.error_log.row_message(
                message=u"Не задана обязательная секция {}".format(
                    self.ACTIVE_TASK)
            )
            raise ConfigApiError

        for item in self.config_parser.options(self.ACTIVE_TASK):
            task_name = self.config_parser.get(self.ACTIVE_TASK, item)
            if not self.check_file_config(task_name):
                self.error_log.row_message(
                    message=u"Секции с именем '{}' "
                            u"не существует ".format(task_name))
                raise ConfigApiError

            task = Task(name=task_name)
            if self.export_key in self.config_parser.options(task.name):
                # Подгрузка опций из секции export
                # Внутри самой секции можно переопределить параметры
                section_name = self.config_parser.get(
                    task.name, self.export_key)
                original_name_task = task.name
                task.name = section_name
                try:
                    self.set_task_prop(task)
                except Exception as error:
                    self.error_log.row_message(
                        message=u"Ошибка при подгрузке"
                                u" секции export : {}".format(error.message))
                    raise ConfigApiError

                task.name = original_name_task

            self.set_task_prop(task)
            self.tasks.append(task)

    def set_task_prop(self, task):
        for option in self.config_parser.options(task.name):
            task.options[option] = self.config_parser.get(task.name, option)
            setattr(task, option, self.config_parser.get(task.name, option))


class Task(object):
    """ Контэйнер для задачи"""
    def __init__(self, **kwargs):
        self.options = {}
        for option in kwargs:
            self.options[option] = kwargs[option]
            setattr(self, option, kwargs[option])

    def __repr__(self):
        return "{{ TASK:{} }}".format(id(self))
