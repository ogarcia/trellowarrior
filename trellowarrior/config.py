#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2015-2020 Óscar García Amor <ogarcia@connectical.com>
#
# Distributed under terms of the GNU GPLv3 license.

from trellowarrior.trellowarriorproject import TrelloWarriorProject
from configparser import RawConfigParser, NoOptionError

import logging
import os

logger = logging.getLogger(__name__)

class Config:
    """
    Configure TrelloWarrior from various sources (with increasing priority)
        - Defaults
        - Config file
        - Supplied config
    """

    def __init__(self):
        # Configure defaults
        self.config_file = None
        self.taskwarrior_taskrc_location = None
        self.taskwarrior_data_location = None
        self.trello_api_key = None
        self.trello_api_secret = None
        self.trello_token = None
        self.trello_token_secret = None
        self.sync_projects = []

    def configure(self, **kwargs):
        # Get config file location
        self.config_file = kwargs.get('config_file', None)
        # No config file passed, search for it in default locations
        if self.config_file == None:
            user_home = os.path.expanduser('~')
            config_home = os.environ.get('XDG_CONFIG_HOME', os.path.join(user_home, '.config'))
            defaults_config_files = [ './trellowarrior.conf',
                    os.path.join(user_home, '.trellowarrior.conf'),
                    os.path.join(config_home, 'trellowarrior/trellowarrior.conf') ]
            config_files = [file for file in defaults_config_files if os.access(file, os.R_OK)]
            self.config_file = config_files[0] if config_files != [] else None

        if self.config_file == None:
            # No config file exists, use XDG_CONFIG location
            self.config_file = os.path.join(config_home, 'trellowarrior/trellowarrior.conf')
            config_directory = os.path.join(config_home, 'trellowarrior')
            # Create config directory if not exists
            if not os.path.exists(config_directory):
                logger.debug('Creating config directory {}'.format(config_directory))
                os.makedirs(config_directory, exist_ok=True)
            logger.debug('No config file exists, using {} as config file'.format(self.config_file))
        elif kwargs.get('parse_config_file', True):
            logger.debug('Using {} as config file'.format(self.config_file))
            # Parse the config
            config_parser = RawConfigParser()
            config_parser.read(self.config_file)

            # Get the TaskWarrior info from config
            self.taskwarrior_taskrc_location = config_parser.get('DEFAULT', 'taskwarrior_taskrc_location', fallback='~/.taskrc')
            self.taskwarrior_data_location = config_parser.get('DEFAULT', 'taskwarrior_data_location', fallback='~/.task')

            # Get the auth info from config
            MandatoryExit = lambda option: SystemExit('Missing mandatory entry \'{}\' in config file'.format(option))
            try:
                self.trello_api_key = config_parser.get('DEFAULT', 'trello_api_key')
            except NoOptionError:
                raise MandatoryExit('trello_api_key')
            try:
                self.trello_api_secret = config_parser.get('DEFAULT', 'trello_api_secret', fallback=None)
            except NoOptionError:
                raise MandatoryExit('trello_api_secret')
            try:
                self.trello_token = config_parser.get('DEFAULT', 'trello_token', fallback=None)
            except NoOptionError:
                raise MandatoryExit('trello_token')
            try:
                self.trello_token_secret = config_parser.get('DEFAULT', 'trello_token_secret', fallback=None)
            except NoOptionError:
                raise MandatoryExit('trello_token_secret')

            # Get the projects to sync
            projects = kwargs.get('projects') if kwargs.get('projects', []) != [] else config_parser.get('DEFAULT', 'sync_projects', fallback='').split()
            for project in projects:
                if config_parser.has_section(project):
                    if not config_parser.has_option(project, 'taskwarrior_project_name') and not config_parser.has_option(project, 'tw_project_name'):
                        logger.warning('Missing mandatory config option \'taskwarrior_project_name\' for sync project \'{}\', ignoring it'.format(project))
                    elif not config_parser.has_option(project, 'trello_board_name'):
                        logger.warning('Missing mandatory config option \'trello_board_name\' for sync project \'{}\', ignoring it'.format(project))
                    else:
                        logger.debug('Configuring project: {}'.format(project))
                        taskwarrior_project_name = config_parser.get(project, 'taskwarrior_project_name', fallback=None)
                        if taskwarrior_project_name is None:
                            logger.warning('Deprecated option \'tw_project_name\' found in \'{}\' project config, you must change it to \'taskwarrior_project_name\' to avoid problems in next release'.format(project))
                            taskwarrior_project_name = config_parser.get(project, 'tw_project_name')
                        lists_filter = config_parser.get(project, 'trello_lists_filter', fallback='').split(',')
                        todo_list = config_parser.get(project, 'trello_todo_list', fallback='To Do')
                        doing_list = config_parser.get(project, 'trello_doing_list', fallback='Doing')
                        done_list = config_parser.get(project, 'trello_done_list', fallback='Done')
                        FilterWarning = lambda basic_list: logger.warning('Cannot add {} list to lists filter, removing it'.format(basic_list))
                        if todo_list in lists_filter:
                            FilterWarning('todo')
                            lists_filter.remove(todo_list)
                        if doing_list in lists_filter:
                            FilterWarning('doing')
                            lists_filter.remove(doing_list)
                        if done_list in lists_filter:
                            FilterWarning('done')
                            lists_filter.remove(done_list)
                        try:
                            only_my_cards = config_parser.getboolean(project, 'only_my_cards', fallback=False)
                        except ValueError:
                            only_my_cards = False
                            logger.warning('Option \'only_my_cards\' is misconfigured in project \'{}\', ignoring it'.format(project))
                        self.sync_projects.append(TrelloWarriorProject(project,
                            taskwarrior_project_name,
                            config_parser.get(project, 'trello_board_name'),
                            trello_todo_list = todo_list,
                            trello_doing_list = doing_list,
                            trello_done_list = done_list,
                            trello_lists_filter = lists_filter,
                            only_my_cards = only_my_cards))
                else:
                    logger.warning('Missing config section for sync project \'{}\', ignoring it'.format(project))
            if self.sync_projects == []:
                raise SystemExit('No projects to sync')

        # Settings from kwargs
        for key, value in kwargs.items():
            if hasattr(self, key) and key != 'config_file':
                setattr(self, key, value)

    def __str__(self):
        return str(self.__dict__)

config = Config()
