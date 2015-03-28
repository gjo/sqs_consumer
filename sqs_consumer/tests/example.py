# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import logging
from ..dispatchers import JsonObjectDispatcher, task


logger = logging.getLogger(__name__)


@task('value')
def test(message):
    logger.info('Dispatched: %r', message)
    return message.get('return', False)


def main(global_config, **settings):
    dispatcher = JsonObjectDispatcher(settings['key_name'])
    dispatcher.scan()
    return dispatcher