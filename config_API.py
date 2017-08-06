#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Обработка API ConfigParser
"""

import sys
import os.path

from ConfigParser import ConfigParser


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
        self.config_parser.readfp(open(self.file_name))

    def read_config(self):
        if self.check_file_exists():
            return
        if not self.check_file_config(*self.requirement_options):
            sys.stdout.write(
                "No required options found")
            return
        for item in self.config_parser.options(self.ACTIVE_TASK):
            if not self.check_file_config(item):
                sys.stdout.write("Not found {}".format(item))
                return
            task = Task(name=item)
            self.set_task_prop(task)
            self.tasks.append(task)

    def set_task_prop(self, task):
        for option in self.config_parser.options(task.name):
            setattr(task, option, self.config_parser.get(task.name, option))


class Task(object):
    """ Контэйнер для задачи"""

    def __init__(self, **kwargs):
        for option in kwargs:
            setattr(self, option, kwargs[option])

    def __repr__(self):
        return "{{ TASK:{} }}".format(id(self))
