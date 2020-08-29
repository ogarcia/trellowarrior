#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2015-2020 Óscar García Amor <ogarcia@connectical.com>
#
# Distributed under terms of the GNU GPLv3 license.

from trellowarrior.config import config
from trellowarrior.configeditor import config_editor
from configparser import NoSectionError, NoOptionError

import logging
import sys

logger = logging.getLogger(__name__)

def parse_option(option):
    # Check if is a default option or a section.option
    if '.' in option:
        try:
            section, option = option.split('.')
        except ValueError:
            raise SystemExit('You can only specify an \'option\' or \'section.option\'{}')
    else:
        section, option = 'DEFAULT', option
    logger.debug('Parsed option to section \'{}\' and option \'{}\''.format(section, option))
    return section, option

def config_get(args):
    section, option = parse_option(args.option)

    # Open config
    config_editor.open(config.config_file)

    # Print value
    try:
        sys.stdout.write('{}\n'.format(config_editor.read(section, option)))
    except NoSectionError:
        raise SystemExit('Section \'{}\' not found in config file'.format(section))
    except NoOptionError:
        raise SystemExit('Option \'{}\' not found in section \'{}\''.format(option, section))

def config_set(args):
    section, option = parse_option(args.option)

    # Open config
    config_editor.open(config.config_file)

    # Save value
    config_editor.write(section, option, args.value)
    config_editor.save()
    logger.info('Added \'{}\' with value \'{}\''.format(args.option, args.value))

def config_remove(args):
    section, option = parse_option(args.option)

    # Open config
    config_editor.open(config.config_file)

    # Remove
    try:
        if config_editor.remove(section, option):
            config_editor.save()
            logger.info('Option \'{}\' removed'.format(args.option))
        else:
            sys.stderr.write('Cannot delete \'{}\', does not exist in config file\n'.format(args.option))
            sys.exit(1)
    except NoSectionError:
        raise SystemExit('Section \'{}\' not found in config file'.format(section))
