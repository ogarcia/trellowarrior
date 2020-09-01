#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2015-2020 Óscar García Amor <ogarcia@connectical.com>
#
# Distributed under terms of the GNU GPLv3 license.

class InvalidOperation(Exception):
    def __init__(self, operation):
        self.operation = operation
        self.message = 'must open config file first'

    def __str__(self):
        return 'Cannot {}, {}'.format(self.operation, self.message)

class ClientError(InvalidOperation):
    def __init__(self, operation):
        self.operation = operation
        self.message = 'must set project first'
