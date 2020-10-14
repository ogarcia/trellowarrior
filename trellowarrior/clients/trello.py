#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2015-2020 Óscar García Amor <ogarcia@connectical.com>
#
# Distributed under terms of the GNU GPLv3 license.

from trellowarrior.exceptions import ClientError
from trello import TrelloClient as Client
from trello.exceptions import ResourceUnavailable

import logging

logger = logging.getLogger(__name__)

class TrelloClient:
    def __init__(self, api_key, api_secret, token, token_secret):
        self.trello_client = Client(api_key=api_key, api_secret=api_secret, token=token, token_secret=token_secret)
        self._uid = None
        self._project = None
        self._board = None
        self._lists = None
        self._board_labels = None
        self._lists_filter = None
        self._only_my_cards = False

    @property
    def whoami(self):
        """
        Get my Trello UID

        :return: my Trello UID
        :rtype: string
        """
        if self._uid is None:
            self._uid = self.trello_client.get_member('me').id
        return self._uid

    def project(self, project):
        """
        Set the class working project

        :param project: TelloWarrior project object
        """
        if self._project == None or self._project.name != project.name:
            self._board = self.get_board(project.trello_board_name)
            self._lists = self.get_lists()
            self._board_labels = self.get_board_labels()
            self._lists_filter = project.trello_lists_filter
            self._only_my_cards = project.only_my_cards

    def get_board(self, board_name):
        """
        Get a open Trello board from name, if it does not exist create it

        :param board_name: the board name
        :return: a Tello board
        :rtype: Trello board object
        """
        for trello_board in self.trello_client.list_boards(board_filter='open'):
            if trello_board.name == board_name and not trello_board.closed:
                logger.debug('Trello board {} found'.format(board_name))
                return trello_board
        logger.debug('Creating Trello board {}'.format(board_name))
        return self.trello_client.add_board(board_name)

    def get_lists(self):
        """
        Get the open lists of a Trello board

        :return: a list of Trello list objects
        :rtype: list
        """
        return self._board.open_lists()

    def get_list(self, list_name):
        """
        Get a Trello list from list name, if it does not exist create it

        :param list_name: the list name
        :return: a Tello list
        :rtype: Trello list object
        """
        if self._lists == None:
            raise ClientError('get_list')
        for trello_list in self._lists:
            if trello_list.name == list_name:
                logger.debug('Trello list {} found'.format(list_name))
                return trello_list
        logger.debug('Creating Trello list {}'.format(list_name))
        trello_list = self._board.add_list(list_name)
        self._lists.append(trello_list) # Update _lists with new list
        return trello_list

    def get_board_labels(self):
        """
        Get the labels of a Trello board

        :param board_name: the board name
        :return: a list of Trello label objects
        :rtype: list
        """
        return self._board.get_labels()

    def get_board_label(self, label_name):
        """
        Get a Trello board label from label name, if it does not exist create it

        :param label_name: the label name
        :return: a Tello label
        :rtype: Trello label object
        """
        if self._board_labels == None:
            raise ClientError('get_board_label')
        for board_label in self._board_labels:
            if board_label.name == label_name:
                logger.debug('Trello board label {} found'.format(label_name))
                return board_label
        logger.debug('Creating Trello board label {}'.format(label_name))
        board_label = self._board.add_label(label_name, 'black')
        self._board_labels.append(board_label) # Update _board_labels with new label
        return board_label

    def get_cards_dict(self):
        """
        Get all cards of a list of Trello lists in a dictionary

        :return: a dict with Cards
        :rtype: dict
        """
        trello_cards_dict = {}
        if self._lists_filter is not None:
            trello_lists = filter(lambda trello_list: trello_list.name not in self._lists_filter, self._lists)
        for trello_list in trello_lists:
            logger.debug('Getting Trello cards of list {}'.format(trello_list.name))
            trello_cards_dict[trello_list.name] = trello_list.list_cards()
            if self._only_my_cards:
                trello_cards_dict[trello_list.name] = filter(lambda trello_card: self.whoami in trello_card.member_ids, trello_cards_dict[trello_list.name])
        return trello_cards_dict

    def delete_card(self, trello_card_id):
        """
        Delete (forever) a Trello card by ID

        :param trello_card_id: ID of Trello card
        """
        try:
            self.trello_client.get_card(trello_card_id).delete()
        except ResourceUnavailable:
            logger.warning('Cannot find Trello card with ID {} deleted in Task Warrior. Maybe you also deleted it in Trello?'.format(trello_card_id))
