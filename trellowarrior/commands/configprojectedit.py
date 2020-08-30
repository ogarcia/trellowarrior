#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2015-2020 Óscar García Amor <ogarcia@connectical.com>
#
# Distributed under terms of the GNU GPLv3 license.

from trellowarrior.config import config
from trellowarrior.configeditor import config_editor
from configparser import NoOptionError

import logging
import sys

logger = logging.getLogger(__name__)

def config_project_list(args):
    # Open config
    config_editor.open(config.config_file)

    # Every config section is a project
    projects = config_editor.list()

    if projects != []:
        projects.sort()
        enabled_projects = config_editor.list_enabled_projects()
        for project in projects:
            # List projects
            status = 'Enabled' if project in enabled_projects else 'Disabled'
            sys.stdout.write('Project \'{}\': {}\n'.format(project, status))
    else:
        sys.stdout.write('No projects declared in config file\n')

def config_project_add(args):
    # Open config
    config_editor.open(config.config_file)

    if config_editor.has_project(args.name):
        sys.stderr.write('A project with name \'{}\' already exists, please use modify command to edit it\n'.format(args.name))
        sys.exit(1)

    if ' ' in args.name:
        sys.stderr.write('A project name must not contain spaces\n')
        sys.exit(1)

    # Add new project
    config_editor.write(args.name, 'taskwarrior_project_name', args.taskwarrior)
    config_editor.write(args.name, 'trello_board_name', args.trello)
    config_editor.write(args.name, 'trello_todo_list', args.todo)
    config_editor.write(args.name, 'trello_doing_list', args.doing)
    config_editor.write(args.name, 'trello_done_list', args.done)
    if args.filter is not None:
        config_editor.write(args.name, 'trello_lists_filter', args.filter)
    if args.only_my_cards:
        config_editor.write(args.name, 'only_my_cards', True)

    if not args.disabled:
        # Add project to enabled projects
        config_editor.enable_project(args.name)

    config_editor.save()
    logger.info('Added {} project \'{}\''.format('disabled' if args.disabled else 'enabled', args.name))

def config_project_modify(args):
    # Check if user provides any option
    if not any([args.taskwarrior, args.trello, args.todo, args.doing, args.done, args.filter, args.only_my_cards]):
        sys.stderr.write('Must provide an option to modify\n')
        sys.exit(1)

    # Open config
    config_editor.open(config.config_file)

    if not config_editor.has_project(args.name):
        sys.stderr.write('Project \'{}\' does not exist in config file\n'.format(args.name))
        sys.exit(1)

    # Modify options
    if args.taskwarrior is not None:
        config_editor.write(args.name, 'taskwarrior_project_name', args.taskwarrior)
    if args.trello is not None:
        config_editor.write(args.name, 'trello_board_name', args.trello)
    if args.todo is not None:
        config_editor.write(args.name, 'trello_todo_list', args.todo)
    if args.doing is not None:
        config_editor.write(args.name, 'trello_doing_list', args.doing)
    if args.done is not None:
        config_editor.write(args.name, 'trello_done_list', args.done)
    if args.filter is not None:
        config_editor.write(args.name, 'trello_lists_filter', args.filter)
    if args.only_my_cards is not None:
        config_editor.write(args.name, 'only_my_cards', True if args.only_my_cards == 'yes' else False)

    config_editor.save()
    logger.info('Project \'{}\' modified'.format(args.name))

def config_project_show(args):
    # Open config
    config_editor.open(config.config_file)

    if not config_editor.has_project(args.name):
        sys.stderr.write('Project \'{}\' does not exist in config file\n'.format(args.name))
        sys.exit(1)

    # List options in project
    try:
        sys.stdout.write('Taskwarrior project name: {}\n'.format(config_editor.read(args.name, 'taskwarrior_project_name')))
    except NoOptionError:
        try:
            sys.stdout.write('Taskwarrior project name (Using DEPRECATED option tw_project_name): {}\n'.format(config_editor.read(args.name, 'tw_project_name')))
        except NoOptionError:
            sys.stdout.write('Warning: missing Taskwarrior project name\n')
    try:
        sys.stdout.write('Trello board name: {}\n'.format(config_editor.read(args.name, 'trello_board_name')))
    except NoOptionError:
        sys.stdout.write('Warning: missing Trello board name\n')
    sys.stdout.write('Trello To Do list: {}\n'.format(config_editor.read(args.name, 'trello_todo_list', 'To Do')))
    sys.stdout.write('Trello Doing list: {}\n'.format(config_editor.read(args.name, 'trello_doing_list', 'Doing')))
    sys.stdout.write('Trello Done list: {}\n'.format(config_editor.read(args.name, 'trello_done_list', 'Done')))
    trello_lists_filter = config_editor.read(args.name, 'trello_lists_filter', '')
    if trello_lists_filter != '':
        sys.stdout.write('Trello lists filter: {}\n'.format(trello_lists_filter))
    try:
        sys.stdout.write('Sync only my cards: {}\n'.format(config_editor.readboolean(args.name, 'only_my_cards')))
    except ValueError:
        sys.stdout.write('Warning: misconfigured only_my_cards option\n')

def config_project_enable(args):
    # Open config
    config_editor.open(config.config_file)

    if not config_editor.has_project(args.name):
        sys.stderr.write('Project \'{}\' does not exist in config file\n'.format(args.name))
        sys.exit(1)

    if config_editor.has_project_enabled(args.name):
        sys.stderr.write('Project \'{}\' is already enabled\n'.format(args.name))
        sys.exit(1)

    # Enable project
    config_editor.enable_project(args.name)
    config_editor.save()
    logger.info('Project \'{}\' enabled'.format(args.name))

def config_project_disable(args):
    # Open config
    config_editor.open(config.config_file)

    # Disable project
    if config_editor.disable_project(args.name):
        config_editor.save()
        logger.info('Project \'{}\' disabled'.format(args.name))
    else:
        sys.stderr.write('Project \'{}\' is already disabled\n'.format(args.name))
        sys.exit(1)

def config_project_remove(args):
    # Open config
    config_editor.open(config.config_file)

    # Remove project
    if config_editor.remove_project(args.name):
        # Disable project too
        config_editor.disable_project(args.name)
        config_editor.save()
        logger.info('Project \'{}\' removed'.format(args.name))
    else:
        sys.stderr.write('Project \'{}\' does not exist in config file\n'.format(args.name))
        sys.exit(1)
