#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2015-2020 Óscar García Amor <ogarcia@connectical.com>
#
# Distributed under terms of the GNU GPLv3 license.

from tasklib.backends import TaskWarrior as Client
from tasklib.task import Task

class TaskwarriorClient:
    def __init__(self, taskrc_location, data_location):
        self.taskwarrior_client = Client(taskrc_location=taskrc_location, data_location=data_location)

    def new_task(self):
        """
        Create a new empty task

        :return: a empty task
        :rtype: Taskwarrior task object
        """
        return Task(self.taskwarrior_client)

    def get_tasks_ids_set(self, project):
        """
        Get a IDs set of pending and completed tasks

        :param project: the project name
        :return: a set of IDs
        :rtype: set
        """
        pending_tasks_ids = set((task['trelloid'] for task in self.taskwarrior_client.tasks.pending().filter(project=project)))
        completed_tasks_ids = set((task['trelloid'] for task in self.taskwarrior_client.tasks.completed().filter(project=project)))
        return pending_tasks_ids | completed_tasks_ids

    def get_pending_tasks(self, project, trelloid=None):
        """
        Get a list of pending tasks in a Taskwarrior project

        :param project: the project name
        :param trelloid: trelloid filter (None by default)
        :return: a list of Taskwarrior tasks objects
        :rtype: list
        """
        return self.taskwarrior_client.tasks.pending().filter(project=project, trelloid=trelloid)

    def get_completed_tasks(self, project, trelloid=None):
        """
        Get a list of completed tasks in a Taskwarrior project

        :param project: the project name
        :param trelloid: trelloid filter (None by default)
        :return: a list of Taskwarrior tasks objects
        :rtype: list
        """
        return self.taskwarrior_client.tasks.completed().filter(project=project, trelloid=trelloid)

    def get_deleted_tasks(self, project):
        """
        Get a list of deleted tasks in a Taskwarrior project

        :param project: the project name
        :return: a list of Taskwarrior tasks objects
        :rtype: list
        """
        return self.taskwarrior_client.tasks.filter(project=project, status='deleted')

    def get_task_by_trello_id(self, trello_id):
        """
        Get a task by Trello ID
        Trello ID must be unique, if not this raise an error

        :param trello_id: Trello card ID
        :return: a Taskwarrior task or None if task not Found
        :rtype: Taskwarrior task object
        """
        tasks = self.taskwarrior_client.tasks.filter(trelloid=trello_id)
        tasks_count = len(tasks)
        if tasks_count == 0:
            return None
        elif tasks_count == 1:
            return tasks[0]
        else:
            raise ValueError('Duplicated Trello ID {} in Taskwarrior tasks. Trello IDs must be unique, please fix it before sync'.format(trello_id))

