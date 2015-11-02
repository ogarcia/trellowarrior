#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2015 Óscar García Amor <ogarcia@connectical.com>
#
# Distributed under terms of the MIT license.

from tasklib.task import TaskWarrior
from trello import TrelloClient

### BEGIN OF CONFIG ### (In next version this go to to configfile)

# Set TaskWarrior
taskwarrior_taskrc_location = '~/.taskrc'
taskwarrior_data_location   = '~/.task'

# Set Trello auth
trello_api_key      = ''
trello_api_secret   = ''
trello_token        = ''
trello_token_secret = ''

# Set sync projects/boards
sync_projects = ['Connectical']

### END OF CONFIG ###

# Create a trello client
trello_client = TrelloClient(api_key=trello_api_key, api_secret=trello_api_secret, token=trello_token, token_secret=trello_token_secret)

def get_trello_boards():
    """ Get all Trello boards """
    trello_boards = trello_client.list_boards()
    if len(trello_boards) > 0:
        return trello_boards
    else:
        return None

def get_tw_project_tasks(project):
    """
    Fetch all tasks from a project

    :project: the project name
    """
    tw_project_tasks = TaskWarrior(taskrc_location=taskwarrior_taskrc_location, data_location=taskwarrior_data_location).tasks.filter(project=project)
    if len(project_tasks) > 0:
        return tw_project_tasks
    else:
        return None

def get_trello_board_id(project):
    """
    Returns Trello board ID from name
    If not exists create it and returns new ID

    :project: the project name
    """
    trello_boards = get_trello_boards()
    if trello_boards:
        for trello_board in trello_boards:
            if trello_board.name == project:
                return trello_board.id
    return create_trello_board(project)

def main():
    for project in sync_projects:
        print (get_trello_board_id(project))

if __name__ == "__main__":
    main()

# Import all tasks into object
#tw = task.TaskWarrior()
#task.TaskWarrior().tasks.filter(project='Connecticale')
#all_tasks = task.TaskWarrior().tasks.all()

# Create a trello client
#trello_client = TrelloClient(api_key=trello_api_key, api_secret=trello_api_secret, token=trello_token, token_secret=trello_token_secret)

# Get all boards in trello (to find tello board id)
#trello_boards = trello_client.list_boards()

def upload_new(project, board_id):
    # Get tasks from project
    project_tasks = task.TaskWarrior().tasks.filter(project=project)
    if len(project_tasks) > 0:

        # Get lists from board
        trello_lists = trello_client.get_board(board_id).open_lists()
        # Get base lists
        todo_list  = None
        doing_list = None
        done_list  = None
        for trello_list in trello_lists:
            if trello_list.name == 'To Do':
                todo_list = trello_list
            if trello_list.name == 'Doing':
                doing_list = trello_list
            if trello_list.name == 'Done':
                done_list = trello_list
        # TODO: Make base lists if not present

        for project_task in project_tasks:
            # If trelloid is empty is a new task crated by taskwarrior
            if not project_task['trelloid']:
                if project_task.completed:
                    new_card = done_list.add_card(project_task['description'])
                    if project_task['due']:
                        new_card.set_due(project_task['due'])
                    print ('Completed')
                    return
                if project_task.active:
                    new_card = doing_list.add_card(project_task['description'])
                    if project_task['due']:
                        new_card.set_due(project_task['due'])
                    print ('Active')
                    return
                new_card = todo_list.add_card(project_task['description'])
                if project_task['due']:
                    new_card.set_due(project_task['due'])
                print ('new')


#def main():
    # Do the samba
#    for project in sync_projects:
        # Try find project - board id correspondence
#        board_id = None
#        for board in trello_boards:
#            if board.name == project:
#                board_id = board.id
#        if not board_id:
            #TODO: Create the board
#            print ('Board not found')
#            return
#        upload_new(project, board_id)
        # Get the board
        #trello_board = trello_client.get_board(board_id)
        # And get lists from board
        #trello_lists = trello_board.open_lists()



