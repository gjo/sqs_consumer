# -*- coding: utf-8 -*-

import logging
import json
import venusian
from pyramid.path import caller_package
from zope.interface import implementer
from .interfaces import IApplication


logger = logging.getLogger(__name__)


@implementer(IApplication)
class DictDispatch(object):

    def __init__(self, key, decoder=json.loads):
        """
        :type key: str
        :type decoder: (bytes) => dict[str, object]
        """
        self.key = key
        self.decoder = decoder
        self.registry = {}
        self.scanner = venusian.Scanner(registry=self.registry)

    def __call__(self, data):
        """
        :type data: bytes
        :return: bool
        """
        decoded = self.decoder(data)
        value = decoded[self.key]
        func = self.registry[value]
        logger.debug('Dispatch Message %s to %s', value, func.__name__)
        return func(decoded)

    def scan(self, package=None):
        if package is None:
            package = caller_package()
        self.scanner.scan(package)


def dict_dispatch_task(value):
    """
    :type value: str
    """
    def wrapper(wrapping):
        """
        :type wrapping: (dict) => bool
        """
        def callback(scanner, name, ob):
            """
            :type scanner: DictDispatch
            :type name: str
            :type ob: object
            """
            scanner.registry[value] = wrapping
        venusian.attach(wrapping, callback)
        return wrapping
    return wrapper
