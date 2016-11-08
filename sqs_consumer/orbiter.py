# -*- coding: utf-8 -*-

import logging
import signal
from pyramid.path import DottedNameResolver
from zope.interface.verify import verifyObject
from .interfaces import ITransport, IWorker


logger = logging.getLogger(__name__)


class Orbiter(object):

    def __init__(self, app, transport, worker):
        """
        :type app: sqs_consumer.interfaces.IApplication
        :type transport: ITransport
        :type worker: IWorker
        """
        self.app = app
        self.transport = transport
        self.worker = worker
        self.stop = False
        self.retval = 0

    def handle_stop(self, sig, frame):
        logger.info('Received signal %r', sig)
        self.stop = True

    def serve_forever(self):
        signal.signal(signal.SIGINT, self.handle_stop)
        signal.signal(signal.SIGQUIT, self.handle_stop)
        signal.signal(signal.SIGTERM, self.handle_stop)
        while not self.stop:
            self.serve_oneshot()

    def serve_oneshot(self):
        self.worker.invoke(self.transport())


def factory(app, config):
    """
    :type app: sqs_consumer.interfaces.IApplication
    :type config: dict
    :return: Orbiter
    """
    resolver = DottedNameResolver(package=None)

    transport_factory = resolver.resolve(config['transport_factory'])
    transport = transport_factory(config)
    verifyObject(ITransport, transport)

    worker_factory = resolver.resolve(config['worker_factory'])
    worker = worker_factory(app, config)
    verifyObject(IWorker, worker)

    return Orbiter(app, transport, worker)
