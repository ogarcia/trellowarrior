#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2015-2020 Óscar García Amor <ogarcia@connectical.com>
#
# Distributed under terms of the GNU GPLv3 license.

from trello.util import create_oauth_token
from trellowarrior.config import config
from configparser import RawConfigParser

import os

def auth(args):
    key = args.api_key or os.environ['TRELLO_API_KEY']
    secret = args.api_key_secret or os.environ['TRELLO_API_SECRET']
    mode = 'r+' if os.path.isfile(config.config_file) else 'w'
    with open(config.config_file, mode) as configfile:
        config_parser = RawConfigParser()
        if mode == 'r+':
            # If file exists read before auth to check it
            config_parser.read_file(configfile)
            configfile.seek(0)

        # Perform auth
        oauth_token = create_oauth_token(expiration=args.expiration, key=key, secret=secret, name=args.name)

        # Write the config
        config_parser.set('DEFAULT', 'trello_api_key', key)
        config_parser.set('DEFAULT', 'trello_api_secret', secret)
        config_parser.set('DEFAULT', 'trello_token', oauth_token['oauth_token'])
        config_parser.set('DEFAULT', 'trello_token_secret', oauth_token['oauth_token_secret'])
        config_parser.write(configfile)
