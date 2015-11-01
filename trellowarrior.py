#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2015 Óscar García Amor <ogarcia@connectical.com>
#
# Distributed under terms of the MIT license.

from tasklib import task
from trello import TrelloClient

# Set Trello auth
trello_api_key      = ''
trello_api_secret   = ''
trello_token        = ''
trello_token_secret = ''

# Set sync projects/boards
sync_projects = ['Connectical']

# Import all tasks into object
#tw = task.TaskWarrior()
#task.TaskWarrior().tasks.filter(project='Connecticale')
all_tasks = task.TaskWarrior().tasks.all()

# Create a trello client
trello_client = TrelloClient(api_key=trello_api_key, api_secret=trello_api_secret, token=trello_token, token_secret=trello_token_secret)

# Get all boards in trello (to find tello board id)
trello_boards = trello_client.list_boards()

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


def main():
    # Do the samba
    for project in sync_projects:
        # Try find project - board id correspondence
        board_id = None
        for board in trello_boards:
            if board.name == project:
                board_id = board.id
        if not board_id:
            #TODO: Create the board
            print ('Board not found')
            return
        upload_new(project, board_id)
        # Get the board
        #trello_board = trello_client.get_board(board_id)
        # And get lists from board
        #trello_lists = trello_board.open_lists()



if __name__ == "__main__":
    main()
