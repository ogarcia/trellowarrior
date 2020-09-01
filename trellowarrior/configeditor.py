#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2015-2020 Óscar García Amor <ogarcia@connectical.com>
#
# Distributed under terms of the GNU GPLv3 license.

from trellowarrior.exceptions import InvalidOperation
from configparser import RawConfigParser, NoOptionError

import logging
import os

logger = logging.getLogger(__name__)

class ConfigEditor:
    def __init__(self):
        self.config_parser = RawConfigParser()
        self.config_file = None

    def open(self, config_file):
        """
        Open and read a config file

        :param config_file: config file path
        """
        logger.debug('Opening {}'.format(config_file))
        self.config_file = config_file
        if os.access(config_file, os.R_OK):
            logger.debug('Parsing config file')
            self.config_parser.read(config_file)

    def read(self, section, option, fallback=None):
        """
        Returns a config option value from config file

        :param section: section where the option is stored
        :param option: option name
        :param fallback: (optional) fallback value
        :return: a config option value
        :rtype: string
        """
        if self.config_file == None:
            raise InvalidOperation('read')
        if fallback is None:
            return self.config_parser.get(section, option)
        else:
            return self.config_parser.get(section, option, fallback=fallback)

    def readboolean(self, section, option, fallback=False):
        """
        Returns a boolean config option value from config file

        :param section: section where the option is stored
        :param option: option name
        :param fallback: (optional) fallback value
        :return: a config option value
        :rtype: boolean
        """
        if self.config_file == None:
            raise InvalidOperation('readboolean')
        return self.config_parser.getboolean(section, option, fallback=fallback)

    def write(self, section, option, value):
        """
        Write a config option value in config object

        :param section: section where the option is stored
        :param option: option name
        :param value: option value
        """
        if self.config_file == None:
            raise InvalidOperation('write')
        if section != 'DEFAULT' and not self.config_parser.has_section(section):
            logger.debug('Adding new section {}'.format(section))
            self.config_parser.add_section(section)
        logger.debug('Adding {}.{} with value {}'.format(section, option, value))
        self.config_parser.set(section, option, value)

    def remove(self, section, option):
        """
        Remove a config option in config object

        :param section: section where the option is stored
        :param option: option name
        :return: True if option is removed, False if not exist
        :rtype: boolean
        """
        if self.config_file == None:
            raise InvalidOperation('remove')
        logger.debug('Removing {}.{}'.format(section, option))
        option_removed = self.config_parser.remove_option(section, option)
        if section != 'DEFAULT' and option_removed:
            if self.config_parser.items(section) == self.config_parser.items('DEFAULT'):
                logger.debug('Removing empty section {}'.format(section))
                self.config_parser.remove_section(section)
        return option_removed

    def remove_project(self, project):
        """
        Remove a project (config section in config object)

        :param project: section name
        :return: True if section is removed, False if not exist
        :rtype: boolean
        """
        if self.config_file == None:
            raise InvalidOperation('remove')
        logger.debug('Removing {}'.format(project))
        return self.config_parser.remove_section(project)

    def list(self):
        """
        List config sections

        :return: list of projects (sections in config)
        :rtype: list
        """
        if self.config_file == None:
            raise InvalidOperation('list')
        return self.config_parser.sections()

    def list_enabled_projects(self):
        """
        Get the list of enabled projects

        :return: list of enabled projects
        :rtype: list
        """
        if self.config_file == None:
            raise InvalidOperation('list_enabled_projects')
        try:
            return self.config_parser.get('DEFAULT', 'sync_projects').split()
        except NoOptionError:
            return []

    def enable_project(self, project):
        """
        Enable a project adding it to sync_projects

        :param project: project name
        """
        if self.config_file == None:
            raise InvalidOperation('enable_project')
        logger.debug('Enabling project {}'.format(project))
        enabled_projects = self.list_enabled_projects()
        enabled_projects.append(project)
        enabled_projects.sort()
        self.config_parser.set('DEFAULT', 'sync_projects', ' '.join(enabled_projects))

    def disable_project(self, project):
        """
        Disable a project removing it from sync_projects

        :param project: project name
        :return: True if project is disabled, False if not
        :rtype: boolean
        """
        if self.config_file == None:
            raise InvalidOperation('disable_project')
        logger.debug('Disabling project {}'.format(project))
        enabled_projects = self.list_enabled_projects()
        try:
            enabled_projects.remove(project)
            self.config_parser.set('DEFAULT', 'sync_projects', ' '.join(enabled_projects))
            return True
        except ValueError:
            logger.debug('Nothing to do, {} is not in enabled projects'.format(project))
            return False

    def has_project(self, project):
        """
        Check if a project (a section in config) is present

        :param project: section name
        :return: True if section exists, False if not
        :rtype: boolean
        """
        if self.config_file == None:
            raise InvalidOperation('has_project')
        return self.config_parser.has_section(project)

    def has_project_enabled(self, project):
        """
        Check if a project is enabled

        :param project: project name
        :return: True if project is enabled, False if not
        :rtype: boolean
        """
        if self.config_file == None:
            raise InvalidOperation('has_project_enabled')
        return True if project in self.list_enabled_projects() else False

    def save(self):
        """
        Save the config object in config file
        """
        if self.config_file == None:
            raise InvalidOperation('save')
        logger.debug('Saving config in config file')
        with open(self.config_file, 'w') as configfile:
            self.config_parser.write(configfile)
        self.config_file = None

    def clean(self):
        """
        Cleans the config editor
        """
        logger.debug('Cleaning config editor')
        self.config_parser = RawConfigParser()
        self.config_file = None

config_editor = ConfigEditor()
