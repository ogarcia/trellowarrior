#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2015 Óscar García Amor <ogarcia@connectical.com>
#
# Distributed under terms of the MIT license.

from ConfigParser import RawConfigParser
from tasklib.task import TaskWarrior
from trello import TrelloClient

def parse_config(config_file):
    """
    Parse config file and return true if all ok
    All config settings are stored in globar vars

    :config_file: config file name
    """
    global trello_api_key, trello_api_secret, trello_token, trello_token_secret
    global taskwarrior_taskrc_location, taskwarrior_data_location
    global sync_projects
    sync_projects = []
    conf = RawConfigParser()
    try:
        conf.read(config_file)
    except Exception:
        return False
    if (not conf.has_option('DEFAULT', 'trello_api_key') or
        not conf.has_option('DEFAULT', 'trello_api_secret') or
        not conf.has_option('DEFAULT', 'trello_token') or
        not conf.has_option('DEFAULT', 'trello_token_secret') or
        not conf.has_option('DEFAULT', 'sync_projects')):
        return False
    for sync_project in conf.get('DEFAULT', 'sync_projects').split():
        if conf.has_section(sync_project):
            if conf.has_option(sync_project, 'tw_project_name') and conf.has_option(sync_project, 'trello_board_name'):
                project = {}
                project['tw_project_name'] = conf.get(sync_project, 'tw_project_name')
                project['trello_board_name'] = conf.get(sync_project, 'trello_board_name')
                if conf.has_option(sync_project, 'trello_todo_list'):
                    project['trello_todo_list'] = conf.get(sync_project, 'trello_todo_list')
                else:
                    project['trello_todo_list'] = 'To Do'
                if conf.has_option(sync_project, 'trello_doing_list'):
                    project['trello_doing_list'] = conf.get(sync_project, 'trello_doing_list')
                else:
                    project['trello_doing_list'] = 'Doing'
                if conf.has_option(sync_project, 'trello_done_list'):
                    project['trello_done_list'] = conf.get(sync_project, 'trello_done_list')
                else:
                    project['trello_done_list'] = 'Done'
                sync_projects.append(project)
            else:
                return False
        else:
            return False
    trello_api_key = conf.get('DEFAULT', 'trello_api_key')
    trello_api_secret = conf.get('DEFAULT', 'trello_api_secret')
    trello_token = conf.get('DEFAULT', 'trello_token')
    trello_token_secret = conf.get('DEFAULT', 'trello_token_secret')
    if conf.has_option('DEFAULT', 'taskwarrior_taskrc_location'):
        taskwarrior_taskrc_location = conf.get('DEFAULT', 'taskwarrior_taskrc_location')
    else:
        taskwarrior_taskrc_location = '~/.taskrc'
    if conf.has_option('DEFAULT', 'taskwarrior_data_location'):
        taskwarrior_data_location = conf.get('DEFAULT', 'taskwarrior_data_location')
    else:
        taskwarrior_data_location = '~/.task'
    return True


def get_trello_boards():
    """ Get all Trello boards """
    trello_client = TrelloClient(api_key=trello_api_key, api_secret=trello_api_secret, token=trello_token, token_secret=trello_token_secret)
    return trello_client.list_boards()

def get_trello_board(board_name):
    """
    Returns Trello board from name
    If does not exist create it and returns new board

    :board_name: the board name
    """
    trello_boards = get_trello_boards()
    for trello_board in trello_boards:
        if trello_board.name == board_name:
            return trello_board
    return create_trello_board(board_name)

def create_trello_board(board_name):
    """
    Create Trello board and returns it

    :board_name: the board name
    """
    trello_client = TrelloClient(api_key=trello_api_key, api_secret=trello_api_secret, token=trello_token, token_secret=trello_token_secret)
    return trello_client.add_board(board_name)

def get_trello_lists(board_name):
    """
    Returns a set of list objects

    :board_name: the board name
    """
    return get_trello_board(board_name).open_lists()

def get_trello_list(board_name, trello_lists, list_name):
    """
    Returns a list object

    :board_name: the board name
    :trello_lists: the set of lists
    :list_name: the list name
    """
    for trello_list in trello_lists:
        if trello_list.name == list_name:
            return trello_list
    return create_trello_list(board_name, list_name)

def create_trello_list(board_name, list_name):
    """
    Returns a new list object from project name and listname

    :board_name: the board name
    :list_name: the list name
    """
    trello_board = get_trello_board(board_name)
    return trello_board.add_list(list_name)

def upload_tw_task(tw_task, trello_list):
    """
    Upload all contents of task to list creating a new card and storing cardid

    :tw_task: TaskWarrior task object
    :trello_list: Trello list object
    """
    new_trello_card = trello_list.add_card(tw_task['description'])
    if tw_task['due']:
        new_trello_card.set_due(tw_task['due'])
    # Save the Trello Card ID into Task
    tw_task['trelloid'] = new_trello_card.id
    tw_task.save()

def get_tw_project_tasks(project_name):
    """
    Fetch all tasks from a project

    :project_name: the project name
    """
    return TaskWarrior(taskrc_location=taskwarrior_taskrc_location, data_location=taskwarrior_data_location).tasks.filter(project=project_name)

def upload_new_tw_tasks(project_name, board_name, todo_list_name, doing_list_name, done_list_name):
    """
    Upload new TaskWarrior tasks that never uploaded before

    :project_name: the project name
    :board_name: the name of Trello board
    :todo_list_name: name of list for todo taks
    :doing_list_name: name of list for active tasks
    :done_list_name: name of list for done tasks
    """
    tw_tasks = get_tw_project_tasks(project_name)
    trello_lists = get_trello_lists(board_name)
    for tw_task in tw_tasks:
        if not tw_task['trelloid']:
            if tw_task.completed:
                upload_tw_task(tw_task, get_trello_list(board_name, trello_lists, done_list_name))
                tw_task['trellolistname'] = done_list_name
                tw_task.save()
            elif tw_task.active:
                upload_tw_task(tw_task, get_trello_list(board_name, trello_lists, doing_list_name))
                tw_task['trellolistname'] = doing_list_name
                tw_task.save()
            else:
                if tw_task['trellolistname']:
                    upload_tw_task(tw_task, get_trello_list(board_name, trello_lists, tw_task['trellolistname']))
                else:
                    upload_tw_task(tw_task, get_trello_list(board_name, trello_lists, todo_list_name))
                    tw_task['trellolistname'] = todo_list_name
                    tw_task.save()

def main():
    for project in sync_projects:
        upload_new_tw_tasks(project['tw_project_name'],
                            project['trello_board_name'],
                            project['trello_todo_list'],
                            project['trello_doing_list'],
                            project['trello_done_list'])
        #print (get_trello_board_id(project))
        #print (get_trello_list(project, 'Movida'))
    #    upload_new_tw_tasks(project)

if __name__ == "__main__":
    if parse_config('trellowarrior.conf'):
        main()
