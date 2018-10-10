#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2015 Óscar García Amor <ogarcia@connectical.com>
#
# Distributed under terms of the MIT license.

try:
    from configparser import RawConfigParser
except ImportError:
    from ConfigParser import RawConfigParser
from tasklib.task import Task
from tasklib.backends import TaskWarrior
from trello import TrelloClient

import argparse
import os

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
        if trello_board.name == board_name and not trello_board.closed:
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
    trello_list = create_trello_list(board_name, list_name)
    trello_lists.append(trello_list) # mutate the list, eek!
    return trello_list

def create_trello_list(board_name, list_name):
    """
    Returns a new list object from project name and listname

    :board_name: the board name
    :list_name: the list name
    """
    trello_board = get_trello_board(board_name)
    return trello_board.add_list(list_name)

def get_trello_dic_cards(trello_lists):
    """
    Returns a dic of lists with a set of card objects in each element

    :trello_lists: the set of lists
    """
    trello_cards = {}
    for trello_list in trello_lists:
        trello_cards[trello_list.name] = trello_list.list_cards()
    return trello_cards

def delete_trello_card(trello_card_id):
    """
    Delete (forever) a Trello Card by ID

    :trello_card_id: Trello card ID
    """
    trello_client = TrelloClient(api_key=trello_api_key, api_secret=trello_api_secret, token=trello_token, token_secret=trello_token_secret)
    try:
        trello_card = trello_client.get_card(trello_card_id)
        trello_card.delete()
    except Exception:
        print('Cannot find Trello card with ID {0} deleted in Task Warrior. Maybe you deleted it in Trello too.'.format(trello_card_id))

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

def download_trello_card(project_name, list_name, trello_card, task_warrior, doing_list_name, done_list_name):
    """
    Download all contens of trello card creating new Task Warrior task

    :project_name: the name of project where the card is stored
    :list_name: the name of list where the card is stored
    :trello_card: a Trello Card object
    :task_warrior: Task Warrior object
    :doing_list_name: name of doing list to set task active
    :done_list_name: name of done list to set task done
    """
    new_tw_task = Task(task_warrior)
    new_tw_task['project'] = project_name
    new_tw_task['description'] = trello_card.name
    if trello_card.due_date:
        new_tw_task['due'] = trello_card.due_date
    new_tw_task['trelloid'] = trello_card.id
    new_tw_task['trellolistname'] = list_name
    new_tw_task.save()
    if list_name == doing_list_name:
        new_tw_task.start()
    if list_name == done_list_name:
        new_tw_task.done()

def get_tw_task_by_trello_id(trello_id):
    """
    Get a task by Trello ID
    Trello ID must be unique, if not this raise an error

    :project_name: the project name
    :trello_id: Trello card ID
    """
    tw_tasks = TaskWarrior(taskrc_location=taskwarrior_taskrc_location, data_location=taskwarrior_data_location).tasks.filter(trelloid=trello_id)
    if len(tw_tasks) == 0:
        return None
    elif len(tw_tasks) == 1:
        return tw_tasks[0]
    else:
        raise ValueError('Duplicated Trello ID {0} in Taskwarrior tasks. Trello IDs must be unique, please fix it before sync.'.format(trello_id))

def upload_new_tw_tasks(trello_lists, project_name, board_name, todo_list_name, doing_list_name, done_list_name):
    """
    Upload new TaskWarrior tasks that never uploaded before

    :trello_lists: the set of lists
    :project_name: the project name
    :board_name: the name of Trello board
    :todo_list_name: name of list for todo taks
    :doing_list_name: name of list for active tasks
    :done_list_name: name of list for done tasks
    """
    task_warrior = TaskWarrior(taskrc_location=taskwarrior_taskrc_location, data_location=taskwarrior_data_location)
    tw_pending_tasks   = task_warrior.tasks.pending().filter(project=project_name, trelloid=None)
    tw_completed_tasks = task_warrior.tasks.completed().filter(project=project_name, trelloid=None)
    for tw_pending_task in tw_pending_tasks:
        if tw_pending_task.active:
            upload_tw_task(tw_pending_task, get_trello_list(board_name, trello_lists, doing_list_name))
            tw_pending_task['trellolistname'] = doing_list_name
            tw_pending_task.save()
        else:
            if tw_pending_task['trellolistname']:
                upload_tw_task(tw_pending_task, get_trello_list(board_name, trello_lists, tw_pending_task['trellolistname']))
            else:
                upload_tw_task(tw_pending_task, get_trello_list(board_name, trello_lists, todo_list_name))
                tw_pending_task['trellolistname'] = todo_list_name
                tw_pending_task.save()
    for tw_completed_task in tw_completed_tasks:
        upload_tw_task(tw_completed_task, get_trello_list(board_name, trello_lists, done_list_name))
        tw_completed_task['trellolistname'] = done_list_name
        tw_completed_task.save()

def sync_trello_tw(trello_lists, project_name, board_name, todo_list_name, doing_list_name, done_list_name):
    """
    Download from Trello all cards and sync with TaskWarrior tasks

    :trello_lists: the set of lists
    :project_name: the project name
    :board_name: the name of Trello board
    :todo_list_name: name of list for todo taks
    :doing_list_name: name of list for active tasks
    :done_list_name: name of list for done tasks
    """
    task_warrior = TaskWarrior(taskrc_location=taskwarrior_taskrc_location, data_location=taskwarrior_data_location)
    # Get all Task Warrior deleted tasks and seek for ones that have trelloid (locally deleted)
    tw_deleted_tasks = task_warrior.tasks.filter(project=project_name,status='deleted')
    for tw_deleted_task in tw_deleted_tasks:
        if tw_deleted_task['trelloid']:
            delete_trello_card(tw_deleted_task['trelloid'])
            tw_deleted_task['trelloid'] = None
            tw_deleted_task.save()
    # Compare and sync Trello with Task Warrior
    trello_dic_cards = get_trello_dic_cards(trello_lists)
    trello_cards_ids = []
    for list_name in trello_dic_cards:
        for trello_card in trello_dic_cards[list_name]:
            # Fech all data from card
            trello_card.fetch(False)
            trello_cards_ids.append(trello_card.id)
            tw_task = get_tw_task_by_trello_id(trello_card.id)
            if tw_task:
                sync_task_card(tw_task, trello_card, board_name, trello_lists, list_name, todo_list_name, doing_list_name, done_list_name)
            else:
                # Download new Trello cards that not present in Task Warrior
                download_trello_card(project_name, list_name, trello_card, task_warrior, doing_list_name, done_list_name)
    # Compare Trello and TaskWarrior tasks for remove deleted Trello tasks in Task Warrior
    tw_pending_tasks_ids   = set((task['trelloid'] for task in task_warrior.tasks.pending().filter(project=project_name)))
    tw_completed_tasks_ids = set((task['trelloid'] for task in task_warrior.tasks.completed().filter(project=project_name)))
    tw_tasks_ids = tw_pending_tasks_ids | tw_completed_tasks_ids
    tw_tasks_ids.discard(None) # Remove None element if present (new tasks created with Task Warrior)
    trello_cards_ids = set(trello_cards_ids)
    deleted_trello_tasks_ids = tw_tasks_ids - trello_cards_ids
    for deleted_trello_task_id in deleted_trello_tasks_ids:
        task_to_delete = get_tw_task_by_trello_id(deleted_trello_task_id)
        task_to_delete['trelloid'] = None
        task_to_delete.save()
        task_to_delete.delete()

def sync_task_card(tw_task, trello_card, board_name, trello_lists, list_name, todo_list_name, doing_list_name, done_list_name):
    """
    Sync existing Trello Card with existing Task Warrior task

    :tw_task: the Task Warrior task object
    :trello_card: the Trello card object
    :board_name: the name of Trello board
    :trello_lists: the set of lists
    :list_name: the name of list where the card is stored
    :todo_list_name: name of list for todo taks
    :doing_list_name: name of list for active tasks
    :done_list_name: name of list for done tasks
    """
    tw_task_modified = False
    # Task description - Trello card name
    if tw_task['description'] != trello_card.name:
        if tw_task['modified'] > trello_card.date_last_activity:
            trello_card.set_name(tw_task['description'])
        else:
            tw_task['description'] = trello_card.name
            tw_task_modified = True
    # Task due - Trello due
    if tw_task['due']:
        if trello_card.due_date:
            if tw_task['modified'] > trello_card.date_last_activity:
                trello_card.set_due(tw_task['due'])
            else:
                tw_task['due'] = trello_card.due_date
                tw_task_modified = True
        else:
            trello_card.set_due(tw_task['due'])
    else:
        if trello_card.due_date:
            tw_task['due'] = trello_card.due_date
            tw_task_modified = True
    # Task List Name / Status - Trello List name
    if tw_task['trellolistname'] == doing_list_name or tw_task['trellolistname'] == done_list_name:
        if tw_task.pending and not tw_task.active and tw_task['modified'] > trello_card.date_last_activity:
            print('Task %s kicked to To Do' % tw_task['id'])
            trello_list = get_trello_list(board_name, trello_lists, todo_list_name)
            trello_card.change_list(trello_list.id)
            tw_task['trellolistname'] = todo_list_name
            list_name = todo_list_name
            tw_task_modified = True
    if tw_task['trellolistname'] != doing_list_name and tw_task.active and tw_task['modified'] > trello_card.date_last_activity:
        print('Task %s kicked to Doing' % tw_task['id'])
        trello_list = get_trello_list(board_name, trello_lists, doing_list_name)
        trello_card.change_list(trello_list.id)
        tw_task['trellolistname'] = doing_list_name
        list_name = doing_list_name
        tw_task_modified = True
    if tw_task['trellolistname'] != done_list_name and tw_task.completed and tw_task['modified'] > trello_card.date_last_activity:
        print('Task %s kicked to Done' % tw_task['id'])
        trello_list = get_trello_list(board_name, trello_lists, done_list_name)
        trello_card.change_list(trello_list.id)
        tw_task['trellolistname'] = done_list_name
        list_name = done_list_name
        tw_task_modified = True
    if tw_task['trellolistname'] != list_name:
        if tw_task['modified'] > trello_card.date_last_activity:
            print('Task %s kicked to Trello list %s' % (tw_task['id'], tw_task['trellolistname']))
            trello_list = get_trello_list(board_name, trello_lists, tw_task['trellolistname'])
            trello_card.change_list(trello_list.id)
        else:
            tw_task['trellolistname'] = list_name
            if list_name == done_list_name:
                print('Task %s kicked to Done' % tw_task['id'])
                if tw_task.completed:
                    tw_task.save()
                    tw_task_modified = False # Set false cause just saved
                else:
                    tw_task.save()
                    tw_task.done()
                    tw_task_modified = False
            elif list_name == doing_list_name:
                print('Task %s kicked to Doing' % tw_task['id'])
                if tw_task.completed:
                    tw_task['status'] = 'pending'
                    tw_task.save()
                    tw_task.start()
                    tw_task_modified = False
                elif tw_task.active:
                    tw_task.save()
                    tw_task_modified = False
                else:
                    tw_task.save()
                    tw_task.start()
                    tw_task_modified = False
            else:
                print('Task %s kicked to %s' % (tw_task['id'], list_name))
                if tw_task.completed:
                    tw_task['status'] = 'pending'
                    tw_task_modified = True
                elif tw_task.active:
                    tw_task.save()
                    tw_task.stop()
                    tw_task_modified = False
                else:
                    tw_task_modified = True
    # Save Task warrior changes (if any)
    if tw_task_modified:
        tw_task.save()

def main():
    parser = argparse.ArgumentParser(description="Bidirectional sync between trello and taskwarrior")
    parser.add_argument('-c', '--config', metavar='value', help='custom configuration file path')
    args = parser.parse_args()

    if args.config == None:
        config_files = [ './trellowarrior.conf',
                os.path.join(os.path.expanduser('~'), '.trellowarrior.conf'),
                os.path.join(os.path.expanduser('~'), '.config/trellowarrior/trellowarrior.conf') ]
        # Try to load one of config default locations
        config_file = [file for file in config_files if os.access(file, os.R_OK)]
        if config_file == []:
            raise SystemExit('No config file found.')
    else:
        config_file = args.config

    if parse_config(config_file):
        for project in sync_projects:
            # Get all Trello lists
            trello_lists = get_trello_lists(project['trello_board_name'])
            # Do sync Trello - Task Warrior
            sync_trello_tw(trello_lists,
                    project['tw_project_name'],
                    project['trello_board_name'],
                    project['trello_todo_list'],
                    project['trello_doing_list'],
                    project['trello_done_list'])
            # Upload new Task Warrior tasks
            upload_new_tw_tasks(trello_lists,
                    project['tw_project_name'],
                    project['trello_board_name'],
                    project['trello_todo_list'],
                    project['trello_doing_list'],
                    project['trello_done_list'])
