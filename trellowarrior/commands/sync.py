#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2015-2020 Óscar García Amor <ogarcia@connectical.com>
#
# Distributed under terms of the GNU GPLv3 license.

from trellowarrior.clients.trellowarrior import TrelloWarriorClient
from trellowarrior.config import config

def sync(args):
    trellowarrior_client = TrelloWarriorClient(config)
    for project in config.sync_projects:
        trellowarrior_client.sync_project(project)
