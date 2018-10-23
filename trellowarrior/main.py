# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2015-2018 Óscar García Amor <ogarcia@connectical.com>
#
# Distributed under terms of the MIT license.
from time import sleep

try:
    from configparser import RawConfigParser
except ImportError:
    from ConfigParser import RawConfigParser
from tasklib.task import Task
from tasklib.backends import TaskWarrior
from trello import TrelloClient
from trello.util import create_oauth_token

import argparse
import os
import logging

logger = logging.getLogger(__name__)


class TwProject(object):
    def __init__(self, tw_project_name, trello_board_name, trello_todo_list='To Do', trello_doing_list='Doing',
                 trello_done_list='Done'):
        self.tw_project_name = tw_project_name
        self.trello_board_name = trello_board_name
        self.trello_todo_list = trello_todo_list
        self.trello_doing_list = trello_doing_list
        self.trello_done_list = trello_done_list

    def is_valid(self):
        return self.tw_project_name is not None and self.trello_board_name is not None


class TrelloWarrior(object):
    CONFIG_FILES = [os.path.join(os.path.expanduser('~'), '.config/trellowarrior/trellowarrior.conf'),
                    os.path.join(os.path.expanduser('~'), '.trellowarrior.conf'),
                    './trellowarrior.conf']

    def __init__(self, config_file=None):
        if config_file:
            self.config_file = config_file
        else:
            for file in TrelloWarrior.CONFIG_FILES:
                if os.access(file, os.R_OK):
                    self.config_file = file  # FIXME keep merging conf file ?
                    break
            else:
                raise SystemExit('No config file found.')
        self.trello_api_key = None
        self.trello_api_secret = None
        self.trello_token = None
        self.trello_token_secret = None
        self.trello_app_name = "TrelloWarrior"
        self.taskwarrior_taskrc_location = '~/.taskrc'
        self.taskwarrior_data_location = '~/.task'
        self.sync_projects = []
        self.all_projects = {}
        self._trello_client = None
        self._trello_boards = None
        self._task_warrior = None
        self.parse_config()

    def validate_config(self):
        res = True
        if (self.trello_api_key is None or
                self.trello_api_secret is None or
                self.trello_token is None or
                self.trello_token_secret is None or
                self.sync_projects is None):
            logger.error('Missing configuration in the default section')
            res = False
        for project_name in self.sync_projects:
            project = self.all_projects.get(project_name)
            if project is None :
                logger.error("Project {} is not defined".format(project))
                res = False
            elif not project.is_valid():
                logger.error("Project {} is not valid, missing required variable".format(project))
                res = False
        return res

    def parse_config(self):
        """
        Parse config file and return true if all ok
        All config settings are stored in globar vars

        :config_file: config file name
        """
        conf = RawConfigParser()
        try:
            conf.read(self.config_file)
        except Exception:
            logger.error("Error while parsing configuration file")
            return
        if conf.has_option('DEFAULT', 'sync_projects'):
            self.sync_projects = conf.get('DEFAULT', 'sync_projects').split()
        for sync_project in conf.sections():
            if conf.has_option(sync_project, 'tw_project_name'):
                tw_project_name = conf.get(sync_project, 'tw_project_name')
            else:
                tw_project_name = None
            if conf.has_option(sync_project, 'trello_board_name'):
                trello_board_name = conf.get(sync_project, 'trello_board_name')
            else:
                trello_board_name = None
            if conf.has_option(sync_project, 'trello_todo_list'):
                trello_todo_list = conf.get(sync_project, 'trello_todo_list')
            else:
                trello_todo_list = 'To Do'
            if conf.has_option(sync_project, 'trello_doing_list'):
                trello_doing_list = conf.get(sync_project, 'trello_doing_list')
            else:
                trello_doing_list = 'Doing'
            if conf.has_option(sync_project, 'trello_done_list'):
                trello_done_list = conf.get(sync_project, 'trello_done_list')
            else:
                trello_done_list = 'Done'
            self.all_projects[sync_project] = TwProject(tw_project_name, trello_board_name, trello_todo_list,
                                                        trello_doing_list, trello_done_list)
        if conf.has_option('DEFAULT', 'trello_api_key'):
            self.trello_api_key = conf.get('DEFAULT', 'trello_api_key')
        if conf.has_option('DEFAULT', 'trello_api_secret'):
            self.trello_api_secret = conf.get('DEFAULT', 'trello_api_secret')
        if conf.has_option('DEFAULT', 'trello_token'):
            self.trello_token = conf.get('DEFAULT', 'trello_token')
        if conf.has_option('DEFAULT', 'trello_token_secret'):
            self.trello_token_secret = conf.get('DEFAULT', 'trello_token_secret')
        if conf.has_option('DEFAULT', 'taskwarrior_taskrc_location'):
            self.taskwarrior_taskrc_location = conf.get('DEFAULT', 'taskwarrior_taskrc_location')
        if conf.has_option('DEFAULT', 'taskwarrior_data_location'):
            self.taskwarrior_data_location = conf.get('DEFAULT', 'taskwarrior_data_location')
        if conf.has_option('DEFAULT', 'trello_app_name'):
            self.trello_app_name = conf.get('DEFAULT', 'trello_app_name')

    def write_config(self):
        conf = RawConfigParser()
        if self.trello_api_key:
            conf.set('DEFAULT', 'trello_api_key', self.trello_api_key)
        if self.trello_api_secret:
            conf.set('DEFAULT', 'trello_api_secret', self.trello_api_secret)
        if self.trello_token:
            conf.set('DEFAULT', 'trello_token', self.trello_token)
        if self.trello_token_secret:
            conf.set('DEFAULT', 'trello_token_secret', self.trello_token_secret)
        conf.set('DEFAULT', 'trello_app_name', self.trello_app_name)
        conf.set('DEFAULT', 'taskwarrior_data_location', self.taskwarrior_data_location)
        conf.set('DEFAULT', 'taskwarrior_taskrc_location', self.taskwarrior_taskrc_location)
        if self.sync_projects:
            conf.set('DEFAULT', 'sync_projects', ' '.join(self.sync_projects))
        for project_name, project in self.all_projects.items():
            conf.add_section(project_name)
            conf.set(project_name, 'trello_board_name', project.trello_board_name)
            conf.set(project_name, 'tw_project_name', project.tw_project_name)
            conf.set(project_name, 'trello_todo_list', project.trello_todo_list)
            conf.set(project_name, 'trello_doing_list', project.trello_doing_list)
            conf.set(project_name, 'trello_done_list', project.trello_done_list)

        with open(self.config_file, 'w') as f:
            conf.write(f)

    @property
    def task_warrior(self):
        """
        Lazy creation of the taskwarrior attribute
        :return: TaskWarrior object
        """
        if self._task_warrior is None:
            self._task_warrior = TaskWarrior(taskrc_location=self.taskwarrior_taskrc_location,
                                             data_location=self.taskwarrior_data_location)
        return self._task_warrior

    @property
    def trello_client(self):
        """
        Lazy creation of the TrelloClient attribute
        :return: TrelloClient object
        """
        if self._trello_client is None:
            self._trello_client = TrelloClient(api_key=self.trello_api_key, api_secret=self.trello_api_secret,
                                               token=self.trello_token, token_secret=self.trello_token_secret)
        return self._trello_client

    def invalid_trello_cache(self):
        """
        Force suppression of trello cache
        """
        self._trello_boards = None

    @property
    def trello_boards(self):
        """
        Lazy load of trello boards

        :return: List of trello boards
        """
        """ Get all Trello boards """
        if self._trello_boards is None:
            logger.debug("Getting all trello boards")
            boards = self.trello_client.list_boards(board_filter="open")
            logger.debug("Boards fetched")
            self._trello_boards = {}
            trello_sync = [p.trello_board_name for p_n, p in self.all_projects.items()
                           if p_n in self.sync_projects]
            for board in boards:
                if board.name in trello_sync:
                    if board.name not in self._trello_boards:
                        self._trello_boards[board.name] = {'board': board, 'lists': None}
        return self._trello_boards

    def get_trello_board(self, board_name):
        """
        Returns Trello board from name
        If does not exist create it and returns new board

        :board_name: the board name
        """
        if board_name not in self.trello_boards:
            self.trello_boards[board_name] = {'board': self.create_trello_board(board_name), 'lists': None}

        board_cache = self.trello_boards[board_name]

        if board_cache['lists'] is None:
            logger.debug("Getting lists for {}".format(board_name))
            board_cache['lists'] = board_cache['board'].open_lists()
            logger.debug("Lists fetched")
        return board_cache

    def create_trello_board(self, board_name):
        """
        Create Trello board and returns it

        :board_name: the board name
        """
        logger.debug("creating board {}".format(board_name))
        return self.trello_client.add_board(board_name)

    def get_trello_list(self, board_name, list_name):
        """
        Returns a list object

        :board_name: the board name
        :trello_lists: the set of lists
        :list_name: the list name
        """
        board_cache = self.get_trello_board(board_name)
        for trello_list in board_cache['lists']:
            if trello_list.name == list_name:
                return trello_list
        trello_list = board_cache['board'].add_list(list_name)
        board_cache['lists'].append(trello_list)
        return trello_list

    def get_trello_dic_cards(self, board_name):
        """
        Returns a dic of lists with a set of card objects in each element for all lists in a board

        :board_name: the board name
        """
        trello_cards = {}
        for trello_list in self.get_trello_board(board_name)['lists']:
            trello_cards[trello_list.name] = trello_list.list_cards()
        return trello_cards

    def delete_trello_card(self, trello_card_id):
        """
        Delete (forever) a Trello Card by ID

        :trello_card_id: Trello card ID
        """
        try:
            trello_card = self.trello_client.get_card(trello_card_id)
            trello_card.delete()
        except Exception:
            print('Cannot find Trello card with ID {0} deleted in Task Warrior. '
                  'Maybe you deleted it in Trello too.'.format(trello_card_id))

    @staticmethod
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

    def download_trello_card(self, project_name, list_name, trello_card, doing_list_name, done_list_name):
        """
        Download all contens of trello card creating new Task Warrior task

        :project_name: the name of project where the card is stored
        :list_name: the name of list where the card is stored
        :trello_card: a Trello Card object
        :task_warrior: Task Warrior object
        :doing_list_name: name of doing list to set task active
        :done_list_name: name of done list to set task done
        """
        new_tw_task = Task(self.task_warrior)
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

    def get_tw_task_by_trello_id(self, trello_id):
        """
        Get a task by Trello ID
        Trello ID must be unique, if not this raise an error

        :project_name: the project name
        :trello_id: Trello card ID
        """
        tw_tasks = self.task_warrior.tasks.filter(trelloid=trello_id)
        if len(tw_tasks) == 0:
            return None
        elif len(tw_tasks) == 1:
            return tw_tasks[0]
        else:
            raise ValueError('Duplicated Trello ID {0} in Taskwarrior tasks. Trello IDs must be unique, please fix'
                             ' it before sync.'.format(trello_id))

    def upload_new_tw_tasks(self, project):
        """
        Upload new TaskWarrior tasks that never uploaded before

        :project: TwProject to sync
        :type project: TwProject
        """
        tw_pending_tasks = self.task_warrior.tasks.pending().filter(project=project.tw_project_name, trelloid=None)
        tw_completed_tasks = self.task_warrior.tasks.completed().filter(project=project.tw_project_name, trelloid=None)
        doing_list = self.get_trello_list(project.trello_board_name, project.trello_doing_list)
        todo_list = self.get_trello_list(project.trello_board_name, project.trello_todo_list)
        done_list = self.get_trello_list(project.trello_board_name, project.trello_done_list)
        for tw_pending_task in tw_pending_tasks:
            if tw_pending_task.active:
                self.upload_tw_task(tw_pending_task, doing_list)
                tw_pending_task['trellolistname'] = project.trello_doing_list
                tw_pending_task.save()
            else:
                if tw_pending_task['trellolistname']:
                    self.upload_tw_task(tw_pending_task, self.get_trello_list(project.trello_board_name,
                                                                              tw_pending_task['trellolistname']))
                else:
                    self.upload_tw_task(tw_pending_task, todo_list)
                    tw_pending_task['trellolistname'] = project.trello_todo_list
                    tw_pending_task.save()
        for tw_completed_task in tw_completed_tasks:
            self.upload_tw_task(tw_completed_task, done_list)
            tw_completed_task['trellolistname'] = project.trello_done_list
            tw_completed_task.save()

    def sync_trello_tw(self, project):
        """
        Download from Trello all cards and sync with TaskWarrior tasks

        :project: TwProject to sync
        :type project: TwProject
        """
        # Get all Task Warrior deleted tasks and seek for ones that have trelloid (locally deleted)
        tw_deleted_tasks = self.task_warrior.tasks.filter(project=project.tw_project_name, status='deleted')
        for tw_deleted_task in tw_deleted_tasks:
            if tw_deleted_task['trelloid']:
                self.delete_trello_card(tw_deleted_task['trelloid'])
                tw_deleted_task['trelloid'] = None
                tw_deleted_task.save()
        # Compare and sync Trello with Task Warrior
        trello_dic_cards = self.get_trello_dic_cards(project.trello_board_name)
        trello_cards_ids = set()
        for list_name in trello_dic_cards:
            for trello_card in trello_dic_cards[list_name]:
                # Fech all data from card
                trello_card.fetch(False)
                trello_cards_ids.add(trello_card.id)
                tw_task = self.get_tw_task_by_trello_id(trello_card.id)
                if tw_task:
                    self.sync_task_card(tw_task, trello_card, project.trello_board_name, list_name,
                                        project.trello_todo_list, project.trello_doing_list, project.trello_done_list)
                else:
                    # Download new Trello cards that not present in Task Warrior
                    self.download_trello_card(project.tw_project_name, list_name, trello_card,
                                              project.trello_doing_list, project.trello_done_list)
        # Compare Trello and TaskWarrior tasks for remove deleted Trello tasks in Task Warrior
        tw_pending_tasks_ids = set((task['trelloid'] for task in
                                    self.task_warrior.tasks.pending().filter(project=project.tw_project_name)))
        tw_completed_tasks_ids = set((task['trelloid'] for task in
                                      self.task_warrior.tasks.completed().filter(project=project.tw_project_name)))
        tw_tasks_ids = tw_pending_tasks_ids | tw_completed_tasks_ids
        tw_tasks_ids.discard(None)  # Remove None element if present (new tasks created with Task Warrior)
        deleted_trello_tasks_ids = tw_tasks_ids - trello_cards_ids
        for deleted_trello_task_id in deleted_trello_tasks_ids:
            task_to_delete = self.get_tw_task_by_trello_id(deleted_trello_task_id)
            task_to_delete['trelloid'] = None
            task_to_delete.save()
            task_to_delete.delete()

    def sync_task_card(self, tw_task, trello_card, board_name, list_name, todo_list_name,
                       doing_list_name, done_list_name):
        """
        Sync existing Trello Card with existing Task Warrior task

        :tw_task: the Task Warrior task object
        :trello_card: the Trello card object
        :board_name: the name of Trello board
        :list_name: the name of list where the card is stored
        :todo_list_name: name of list for todo tasks
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
                logger.info('Task %s kicked to To Do' % tw_task['id'])
                trello_list = self.get_trello_list(board_name, todo_list_name)
                trello_card.change_list(trello_list.id)
                tw_task['trellolistname'] = todo_list_name
                list_name = todo_list_name
                tw_task_modified = True
        if tw_task['trellolistname'] != doing_list_name and tw_task.active and \
                tw_task['modified'] > trello_card.date_last_activity:
            logger.info('Task %s kicked to Doing' % tw_task['id'])
            trello_list = self.get_trello_list(board_name, doing_list_name)
            trello_card.change_list(trello_list.id)
            tw_task['trellolistname'] = doing_list_name
            list_name = doing_list_name
            tw_task_modified = True
        if tw_task['trellolistname'] != done_list_name and tw_task.completed and \
                tw_task['modified'] > trello_card.date_last_activity:
            logger.info('Task %s kicked to Done' % tw_task['id'])
            trello_list = self.get_trello_list(board_name, done_list_name)
            trello_card.change_list(trello_list.id)
            tw_task['trellolistname'] = done_list_name
            list_name = done_list_name
            tw_task_modified = True
        if tw_task['trellolistname'] != list_name:
            if tw_task['modified'] > trello_card.date_last_activity:
                logger.info('Task %s kicked to Trello list %s' % (tw_task['id'], tw_task['trellolistname']))
                trello_list = self.get_trello_list(board_name, tw_task['trellolistname'])
                trello_card.change_list(trello_list.id)
            else:
                tw_task['trellolistname'] = list_name
                if list_name == done_list_name:
                    logger.info('Task %s kicked to Done' % tw_task['id'])
                    if tw_task.completed:
                        tw_task.save()
                        tw_task_modified = False  # Set false cause just saved
                    else:
                        tw_task.save()
                        tw_task.done()
                        tw_task_modified = False
                elif list_name == doing_list_name:
                    logger.info('Task %s kicked to Doing' % tw_task['id'])
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
                    logger.info('Task %s kicked to %s' % (tw_task['id'], list_name))
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

    def sync(self, projects=None):
        """
        Sync all projects defined in the config or those given as a parameters

        :param projects: List of projects to sync. If not specified use list of projects from conf file
        :return:
        """
        if projects is None:
            projects = self.sync_projects
        logger.debug("Will sync {}".format(projects))
        if self.validate_config():
            for project_name in projects:
                logger.info("Syncing {}".format(project_name))
                project = self.all_projects[project_name]
                logger.debug("Do sync Trello - Task Warrior")
                self.sync_trello_tw(project)
                logger.debug("Upload new Task Warrior tasks")
                self.upload_new_tw_tasks(project)
            logger.debug("All projects synced")

    def authenticate(self, expiration=None, api_key=None, api_secret=None, name=None):
        """
        Authenticate against trello and store the token in the config file

        :param expiration: Can be set to 1hour, 1day, 30days, never. If not set will be read
        from TRELLO_EXPIRATION environment variable
        :param api_key: Trello api key. If not set will be read from the config file or from TRELLO_API_KEY
        environment variable.
        :param api_secret: trello api secret. If not set will be read from the config file or from TRELLO_API_SECRET
        environment variable.
        :param name: Trello application name. If not set will be read from the config file or from TRELLO_NAME
        environment variable.
        """
        if api_key:
            self.trello_api_key = api_key
        if api_secret:
            self.trello_api_secret = api_secret
        if name:
            self.trello_app_name = name
        oauth_token = create_oauth_token(expiration=expiration, key=self.trello_api_key, secret=self.trello_api_secret,
                                         name=self.trello_app_name)
        self.trello_token = oauth_token['oauth_token']
        self.trello_token_secret = oauth_token['oauth_token_secret']
        self.write_config()

    def new_project(self, name, tw_project_name, trello_board_name, trello_todo_list='To Do', trello_doing_list='Doing',
                    trello_done_list='Done', no_sync=False):
        """
        Add a new project to the config

        :param name: name of the project in the config
        :param tw_project_name: name of the corresponding taskwarrior project
        :param trello_board_name: name of the corresponding trello board
        :param trello_todo_list: name of the todo list in trello
        :param trello_doing_list: name of the doing list in trello
        :param trello_done_list: name of the done list in trello
        :param no_sync: Do not add the project to the list of projects to sync if set to true
        """
        project = TwProject(tw_project_name, trello_board_name, trello_todo_list, trello_doing_list, trello_done_list)
        self.all_projects[name] = project
        if not no_sync:
            self.sync_projects.append(name)
        self.write_config()


def sync(args):
    """
    Function called by the sync subcomand to perform the sync between trello and taskwarrior

    :args: command line arguments. Must contain a 'config' attribute
    """
    tw = TrelloWarrior(config_file=args.config)
    if args.projects:
        projects = args.projects
    else:
        projects = None
    tw.sync(projects)
    seconds = args.delai_between_sync * 60
    if seconds > 0:
        try:
            while True:
                logger.info("Sync done. will wait {} minutes before next one "
                            "(press ctrl-c to stop)".format(args.delai_between_sync))
                sleep(seconds)
                tw.invalid_trello_cache()
                tw.sync(projects)
        except KeyboardInterrupt:
            pass

def authenticate(args):
    """
    Function called by the authenticate subcommand to perform the initial authentication

    :args: Command line arguments. Must contain the following attributes : 'config', 'api_key', 'api_key_secret', 'name'
    """
    tw = TrelloWarrior(config_file=args.config)
    tw.authenticate(args.expiration, args.api_key, args.api_key_secret, args.name)


def new_project(args):
    """
    Function called by the new subcommand to add a project to the config

    :args: Command line arguments. Must contain the following attributes : 'config', 'name', 'tw_name', 'board_name',
            'todo', 'doing', 'done', 'no_sync'
    """
    tw = TrelloWarrior(config_file=args.config)
    tw.new_project(args.name, args.tw_name, args.board_name, args.todo, args.doing, args.done, args.no_sync)


def main():
    parser = argparse.ArgumentParser(description="Bidirectional sync between trello and taskwarrior")
    parser.add_argument('-c', '--config', metavar='value', help='custom configuration file path')
    parser.add_argument('-v', '--verbose', help='Increase verbosity. Can be repeated up to 2 times', action='count')
    subparsers = parser.add_subparsers()
    sync_parser = subparsers.add_parser('sync', help="Synchronize trello and taskwarrior")
    sync_parser.add_argument("projects", nargs='*',
                             help="List of projects to synchronize. If empty will synchronize all projects listed in "
                                  "the configuration file")
    sync_parser.add_argument("--delai-between-sync", '-d', metavar='N', default=0, type=int,
                             help="Launch the sync process every N minutes. If set to 0 (default), perform one sync and"
                                  " exit.")
    sync_parser.set_defaults(func=sync)
    new_parser = subparsers.add_parser('new', help="Add a new project to the config file,"
                                                    " override existing one if present")
    new_parser.add_argument('name', help='section name in config file')
    new_parser.add_argument('board_name', help='Trello board name')
    new_parser.add_argument('tw_name', help='Taskwarrior project name')
    new_parser.add_argument('--todo', help='Todo trello list name, default to %(default)s', default='To Do')
    new_parser.add_argument('--doing', help='Doing trello list name, default to %(default)s', default='Doing')
    new_parser.add_argument('--done', help='Todo trello list name, default to %(default)s', default='Done')
    new_parser.add_argument('--no-sync', help='Deactivate auto sync for this project '
                                              '(it will not be in the sync_project list)')
    new_parser.set_defaults(func=new_project)
    auth_parser = subparsers.add_parser('authenticate',
                                        help="Setup the authentication against trello. Store the parameters "
                                             "in the file given with the '--config' argument or the first default"
                                             " config file found. If no file exists, the -c argument must be used.")
    auth_parser.add_argument("--api-key", help="Your api key. Get it from https://trello.com/app-key. "
                                               "If not set will be read from the config file or from "
                                               "TRELLO_API_KEY environment variable.")
    auth_parser.add_argument("--api-key-secret",
                             help="Your api key secret. Get it from https://trello.com/app-key. "
                                  "If not set will be read from the config file or from "
                                  "TRELLO_API_SECRET environment variable.")
    auth_parser.add_argument("--name", help="Trello application name. If not set will be read from the config file or "
                                            "from TRELLO_NAME environment variable.")
    auth_parser.add_argument("--expiration", help="Can be set to 1hour, 1day, 30days, never. If not set will be read "
                                                  "from TRELLO_EXPIRATION environment variable.")
    auth_parser.set_defaults(func=authenticate)
    args = parser.parse_args()
    ch = logging.StreamHandler()
    if args.verbose > 1:
        logger.setLevel(logging.DEBUG)
    elif args.verbose == 1:
        logger.setLevel(logging.INFO)
    else:
        logger.setLevel(logging.WARNING)
    ch.setFormatter(logging.Formatter('%(asctime)s\t- %(levelname)s\t- %(message)s'))
    logger.addHandler(ch)
    args.func(args)
