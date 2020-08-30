#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2015-2020 Óscar García Amor <ogarcia@connectical.com>
#
# Distributed under terms of the GNU GPLv3 license.

from trellowarrior.commands.auth import auth
from trellowarrior.commands.configedit import config_get, config_set, config_remove
from trellowarrior.commands.configprojectedit import config_project_list, config_project_add, config_project_modify, config_project_show
from trellowarrior.commands.configprojectedit import config_project_enable, config_project_disable, config_project_remove
from trellowarrior.commands.sync import sync
from trellowarrior.commands.version import version
from trellowarrior.config import config

import argparse
import logging
import os

def main():
    # Set loglevel equivalents for argument parser
    log_levels = {
            0: logging.WARNING,
            1: logging.INFO,
            2: logging.DEBUG }

    # Create argument parser to get options via arguments
    parser = argparse.ArgumentParser(description='Bidirectional sync between Trello and Taskwarrior')
    parser.add_argument('-c', '--config', metavar='value', help='custom configuration file path')
    parser.add_argument('-v', '--verbose', action='count', default=0, help='be verbose (add more v to increase verbosity)')
    parser.set_defaults(func=sync) # Perform sync if no command given
    parser.set_defaults(projects=[]) # No forced projects by default
    subparsers = parser.add_subparsers(dest='command')
    subparsers.required = False

    sync_parser = subparsers.add_parser('sync', help='synchronize Trello and Taskwarrior')
    sync_parser.add_argument('projects', nargs='*', help='list of projects to synchronize, if empty will synchronize all enabled projects')
    sync_parser.set_defaults(func=sync)

    auth_parser = subparsers.add_parser('auth', help='setup the authentication against Trello')
    auth_parser.add_argument('--api-key', help='your API Key, can be set from TRELLO_API_KEY environment variable')
    auth_parser.add_argument('--api-key-secret', help='your API Key secret, can be set from TRELLO_API_SECRET environment variable')
    auth_parser.add_argument('--expiration', choices=['1hour', '1day', '30days', 'never'], help='duration of authorization, can be set from TRELLO_EXPIRATION environment variable')
    auth_parser.add_argument('--name', default=os.environ.get('TRELLO_NAME', 'TrelloWarrior'), help='application name, can be set from TRELLO_NAME environment variable, current default: %(default)s')
    auth_parser.set_defaults(func=auth)

    config_parser = subparsers.add_parser('config', help='view or modify TrelloWarrior config')
    config_subparsers = config_parser.add_subparsers(dest='config_subcommand')
    config_subparsers.required = True

    config_get_parser = config_subparsers.add_parser('get', help='get a config value')
    config_get_parser.add_argument('option', help='name of config option, use section.option to get config values outside of default section')
    config_get_parser.set_defaults(func=config_get)

    config_set_parser = config_subparsers.add_parser('set', help='set new or modify a config value')
    config_set_parser.add_argument('option', help='name of config option, use section.option to set config values outside of default section')
    config_set_parser.add_argument('value', help='config value')
    config_set_parser.set_defaults(func=config_set)

    config_remove_parser = config_subparsers.add_parser('remove', help='remove a config value')
    config_remove_parser.add_argument('option', help='name of config option, use section.option to remove config values outside of default section')
    config_remove_parser.set_defaults(func=config_remove)

    config_project_parser = config_subparsers.add_parser('project', help='configure projects')
    config_project_subparsers = config_project_parser.add_subparsers(dest='config_project_subcommand')
    config_project_subparsers.required = True

    config_project_list_parser = config_project_subparsers.add_parser('list', help='list projects')
    config_project_list_parser.set_defaults(func=config_project_list)

    config_project_add_parser = config_project_subparsers.add_parser('add', help='add new project')
    config_project_add_parser.add_argument('name', help='project name')
    config_project_add_parser.add_argument('taskwarrior', help='project name in Taskwarrior')
    config_project_add_parser.add_argument('trello', help='project name in Trello')
    config_project_add_parser.add_argument('--todo', default='To Do', help='to do Trello list name, default: %(default)s')
    config_project_add_parser.add_argument('--doing', default='Doing', help='doing Trello list name, default: %(default)s')
    config_project_add_parser.add_argument('--done', default='Done', help='done Trello list name, default: %(default)s')
    config_project_add_parser.add_argument('--filter', help='Trello lists to filter on sync (separated by commas)')
    config_project_add_parser.add_argument('-o', '--only-my-cards', action='store_true', help='sync only cards assigned to me')
    config_project_add_parser.add_argument('-d', '--disabled', action='store_true', help='add project disabled')
    config_project_add_parser.set_defaults(func=config_project_add)

    config_project_modify_parser = config_project_subparsers.add_parser('modify', help='modify values of existing project')
    config_project_modify_parser.add_argument('name', help='project name')
    config_project_modify_parser.add_argument('--taskwarrior', help='project name in Taskwarrior')
    config_project_modify_parser.add_argument('--trello', help='project name in Trello')
    config_project_modify_parser.add_argument('--todo', help='to do Trello list name')
    config_project_modify_parser.add_argument('--doing', help='doing Trello list name')
    config_project_modify_parser.add_argument('--done', help='done Trello list name')
    config_project_modify_parser.add_argument('--filter', help='Trello lists to filter on sync (separated by commas)')
    config_project_modify_parser.add_argument('--only-my-cards', choices=['yes', 'no'], help='sync only cards assigned to me')
    config_project_modify_parser.set_defaults(func=config_project_modify)

    config_project_show_parser = config_project_subparsers.add_parser('show', help='show project configuration')
    config_project_show_parser.add_argument('name', help='project name')
    config_project_show_parser.set_defaults(func=config_project_show)

    config_project_enable_parser = config_project_subparsers.add_parser('enable', help='enable existing project sync')
    config_project_enable_parser.add_argument('name', help='project name')
    config_project_enable_parser.set_defaults(func=config_project_enable)

    config_project_disable_parser = config_project_subparsers.add_parser('disable', help='disable existing project sync')
    config_project_disable_parser.add_argument('name', help='project name')
    config_project_disable_parser.set_defaults(func=config_project_disable)

    config_project_remove_parser = config_project_subparsers.add_parser('remove', help='remove existing project')
    config_project_remove_parser.add_argument('name', help='project name')
    config_project_remove_parser.set_defaults(func=config_project_remove)

    parser_version = subparsers.add_parser('version', help='show TrelloWarrior version')
    parser_version.set_defaults(func=version)

    args = parser.parse_args()

    # Maximum loglevel is 3 if user sends more vvv we ignore it
    args.verbose = 2 if args.verbose >= 2 else args.verbose

    # Set loglevel via argument or environment (untouched warning by default)
    log_level = log_levels[args.verbose]
    logging.basicConfig(level=log_level)
    logger = logging.getLogger('TrelloWarrior')
    logger.info('Setting loglevel to {}'.format(logging.getLevelName(log_level)))

    # Configure app
    if args.command in ['sync', None]:
        # Need full parse and check configuration for sync (or for no arguments which implies sync)
        config.configure(config_file=args.config, projects=args.projects)
    elif args.command != 'version':
        # Don't need parse condfiguration for rest of commands
        config.configure(config_file=args.config, parse_config_file=False)

    # Run main app
    args.func(args)
