# -*- coding: utf-8 -*-

from zope.interface import Attribute, Interface


class IApplication(Interface):
    def __call__(data):
        """
        Return true if processes for `data` is done and worker can
        remove message from broker.

        :type data: str
        :rtype: bool
        """


class IMessage(Interface):
    # :type: bytes
    id = Attribute('Message Id')

    # :type: bytes
    body = Attribute('Message Body')

    # :type: bytes
    receipt_handle = Attribute('Message Receipt Handle')

    def delete():
        """
        Delete this message from queue.
        """


class ITransport(Interface):
    def __call__():
        """
        :rtype: collections.Iterable[IMessage]
        """


class IWorker(Interface):
    def invoke(messages):
        """
        :type messages: collections.Iterable[IMessage]
        """
