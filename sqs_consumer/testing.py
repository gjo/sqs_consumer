# -*- coding: utf-8 -*-

import logging
from mock import Mock
from zope.interface import classImplements
from .interfaces import IApplication, IMessage, ITransport, IWorker


logger = logging.getLogger(__name__)


# http://programmaticallyspeaking.com/mocking-zope-interfaces.html
def _iface_mock(iface):
    """
    :type iface: zope.interface.Interface
    :rtype: Mock
    """

    def init(self, *args, **kwargs):
        Mock.__init__(self, spec=list(iface.names()), *args, **kwargs)

    name = iface.__name__ + 'Mock'
    cls = type(name, (Mock,), {'__init__': init})
    classImplements(cls, iface)
    # globals()[name] = cls
    return cls  # for IDE support


IApplicationMock = _iface_mock(IApplication)
IMessageMock = _iface_mock(IMessage)
ITransportMock = _iface_mock(ITransport)
IWorkerMock = _iface_mock(IWorker)


def dummy_sqs_message():
    """
    :rtype: dict[bytes, bytes]
    """
    return {
        'MessageId': '__dummy_id__',
        'Body': '__dummy_body__',
        'ReceiptHandle': '__dummy_receipt_handle__',
    }


def sqs_client_mock():
    """
    :rtype: Mock
    """
    client = Mock(spec=['delete_message', 'get_queue_url', 'receive_message'])
    client.get_queue_url.return_value = {'QueueUrl': '__dummy_url__'}
    return client


def transport_mock_factory(config, prefix='transport.mock.'):
    """
    :type config: dict
    :type prefix: str
    :rtype: ITransport
    """
    transport = ITransportMock()
    return transport


def worker_mock_factory(app, config, prefix='worker.mock.'):
    """
    :type app: callable
    :type config: dict
    :type prefix: str
    :rtype: IWorker
    """
    worker = IWorkerMock()
    return worker


def example_app_factory(global_config, **settings):  # pragma: nocover
    from .dispatchers import JsonObjectDispatcher
    app = JsonObjectDispatcher(key='key')

    def example_task(data):
        logger.info('Dispatched: %r', data)
        return data.get('return', False)

    app.registry.add('value', example_task)
    return app
