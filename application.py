#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    Приложние
"""
import os
from config_API import ConfigAPI
from trigger import (
    GTEDateModifyTrigger, AllCopiesGTEOlderTriggerOrNotExists,
    FileNotExistsTrigger, FileExistsTrigger,
    RegularExpressionFolderNotExits, RegularExpressionFolderExits,
    RegularExpressionFileNotExits, RegularExpressionFileExits,
    AllWaysTrueTrigger
)
from datetime import datetime


class Application(object):
    """
    Само приложение
    """
    file_name = "mail_sender.conf"
    conf = ConfigAPI(file_name)
    conf.read_config()

    for task in iter(conf.tasks):
        options = {
            'message_title': task.project_name,
            'message_body': task.trigger_event,
            'from_address': task.from_address,
            'to_address': task.to_address,
            'SMTP_host': task.smtp_host,
            'SMTP_port': task.smtp_port,
            'password': task.password
        }
        if task.trigger_type == 'GTEDateModifyTrigger':
            Event = GTEDateModifyTrigger(
                task.triggered_file,
                datetime.fromtimestamp(
                    os.path.getmtime(
                        task.triggered_file)).strftime('%Y-%m-%d'),
                int(task.gte_days),
                **options
            )
        if task.trigger_type == 'AllCopiesGTEOlderTriggerOrNotExists':
            Event = AllCopiesGTEOlderTriggerOrNotExists(
                task.path,
                task.mask,
                int(task.gte_days),
                **options
            )
        if task.trigger_type == 'FileNotExistsTrigger':
            Event = FileNotExistsTrigger(task.path_file_name, **options)

        if task.trigger_type == 'FileExistsTrigger':
            Event = FileExistsTrigger(task.path_file_name, **options)

        if task.trigger_type == 'RegularExpressionFolderNotExits':
            Event = RegularExpressionFolderNotExits(
                task.path, task.mask, **options)

        if task.trigger_type == 'RegularExpressionFolderExits':
            Event = RegularExpressionFolderExits(
                task.path, task.mask, **options)

        if task.trigger_type == 'RegularExpressionFileNotExits':
            Event = RegularExpressionFileNotExits(
                task.path, task.mask, **options)

        if task.trigger_type == 'RegularExpressionFileExits':
            Event = RegularExpressionFileExits(task.path, task.mask, **options)

        if task.trigger_type == 'AllWaysTrueTrigger':
            Event = AllWaysTrueTrigger(**options)

        Event.run()


if __name__ == "__main__":
    u""" Зупуск приложения """
    Application_instance = Application()
