#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2015-2020 Óscar García Amor <ogarcia@connectical.com>
#
# Distributed under terms of the GNU GPLv3 license.

class TrelloWarriorProject:
    def __init__(self, name, taskwarrior_project_name, trello_board_name, **kwargs):
        self.name = name
        self.taskwarrior_project_name = taskwarrior_project_name
        self.trello_board_name = trello_board_name
        self.trello_todo_list = kwargs.get('trello_todo_list', 'To Do')
        self.trello_doing_list = kwargs.get('trello_doing_list', 'Doing')
        self.trello_done_list = kwargs.get('trello_done_list', 'Done')
        self.trello_lists_filter = kwargs.get('trello_lists_filter', None)
        self.only_my_cards = kwargs.get('only_my_cards', False)

    def __repr__(self):
        return '<TrelloWarriorProject {}>'.format(self.name)

    def __str__(self):
        return str(self.__dict__)
