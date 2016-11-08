# -*- coding: utf-8 -*-

import logging
from zope.interface import implementer
from .interfaces import IWorker


logger = logging.getLogger(__name__)


@implementer(IWorker)
class SyncWorker(object):

    def __init__(self, app):
        """
        :type app: sqs_consumer.interfaces.IApplication
        """
        self.app = app

    def invoke(self, messages):
        """
        :type messages: collections.Iterable[sqs_consumer.interfaces.IMessage]
        """
        for message in messages:
            logger.info('Process Message: %s', message.id)
            ret = None
            try:
                ret = self.app(message.body)
            except:
                logger.exception('Application Halted: %r', message)
            if ret:
                message.delete()


def sync_factory(app, settings, prefix='worker.sync.'):
    """
    :type app: sqs_consumer.interfaces.IApplication
    :type settings: dict[str, str]
    :type prefix: str
    :rtype: SyncWorker
    """
    return SyncWorker(app)
