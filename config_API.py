#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Обработка API ConfigParser
"""
import codecs
import os.path
import sys
from ConfigParser import ConfigParser

from trigger import FLAG_READ_FILE

UTF_WITH_BOM = 'utf-8-sig'


class ConfigAPI(object):
    """ API для создания триггеров """

    config_parser = ConfigParser()
    ACTIVE_TASK = 'active_task'
    requirement_options = [ACTIVE_TASK]

    TRIGGER_TYPE = 'trigger_type'
    MESSAGE = 'message'
    GTE_DAYS = 'GTE_DAYS'

    tasks = []

    def __init__(self, file_name):
        self.file_name = file_name
        pass

    def check_file_config(self, *sections):
        """ Проверка обязательных секций  """

        return all(
            self.config_parser.has_section(section) for section in sections)

    def check_file_exists(self):
        """ Проверка существует ли файл """
        if not (os.path.isfile(self.file_name)):
            sys.stdout.write("File does not exists {}".format(self.file_name))
            return False
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
            sys.stdout.write(
                "No required options found")
            return
        for item in self.config_parser.options(self.ACTIVE_TASK):
            task_name = self.config_parser.get(self.ACTIVE_TASK, item)
            if not self.check_file_config(task_name):
                sys.stdout.write("Not found {}".format(task_name))

            task = Task(name=task_name)
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
        # TODO для лога нужно больше деталей
        # TODO v 0.2
        return "{{ TASK:{} }}".format(id(self))
