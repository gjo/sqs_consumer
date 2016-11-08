# -*- coding: utf-8 -*-

import logging
import botocore
import botocore.session
from zope.interface import implementer
from .interfaces import IMessage, ITransport


logger = logging.getLogger(__name__)


@implementer(IMessage)
class BotoCoreMessage(object):

    def __init__(self, transport, data):
        """
        :type transport: BotoCoreTransport
        :type data: dict[bytes, bytes]
        """
        self.transport = transport
        self.data = data

    # :type: bytes
    id = property(lambda self: self.data['MessageId'])

    # :type: bytes
    body = property(lambda self: self.data['Body'])

    # :type: bytes
    receipt_handle = property(lambda self: self.data['ReceiptHandle'])

    def delete(self):
        self.transport.delete_message(self.data)


@implementer(ITransport)
class BotoCoreTransport(object):

    def __init__(self, queue_name, client, receive_params):
        """
        :type queue_name: str
        :type client: botocore.client.sqs
        :type receive_params: dict
        """
        self.queue_name = queue_name
        self.client = client
        self.receive_params = receive_params
        self.queue_url = self.get_queue_url()

    def __call__(self):
        """
        :rtype: collections.Iterable[BotoCoreMessage]
        """
        ret = self.receive_message()
        if 'Messages' in ret:
            logger.info('Polled: %d messages', len(ret['Messages']))
            for m in ret['Messages']:
                yield BotoCoreMessage(self, m)
        else:
            logger.info('Polled: no messages')

    def get_queue_url(self):
        """
        :rtype: str
        """
        params = dict(QueueName=self.queue_name)
        logger.debug('[PROTO] GetQueueUrl Call: %r', params)
        ret = self.client.get_queue_url(**params)
        logger.debug('[PROTO] GetQueueUrl Return: %r', ret)
        return ret['QueueUrl']

    def receive_message(self):
        """
        :rtype: dict
        """
        params = dict(QueueUrl=self.queue_url)
        params.update(self.receive_params)
        logger.debug('[PROTO] ReceiveMessage Call: %r', params)
        ret = self.client.receive_message(**params)
        logger.debug('[PROTO] ReceiveMessage Return: %r', ret)
        return ret

    def delete_message(self, message):
        """
        :type message: BotoCoreMessage
        :rtype: dict
        """
        params = dict(QueueUrl=self.queue_url,
                      ReceiptHandle=message.receipt_handle)
        logger.debug('[PROTO] DeleteMessage Call: %r', params)
        ret = self.client.delete_message(**params)
        logger.debug('[PROTO] DeleteMessage Return: %r', ret)
        return ret


def botocore_factory(settings, prefix='transport.botocore.'):
    """
    :type settings: dict
    :type prefix: str
    :rtype: BotoCoreTransport
    """
    st = dict([(k[len(prefix):], v) for k, v in settings.items()
               if k.startswith(prefix)])

    queue_name = st['queue_name']

    sv = dict([(k[len('session_vars.'):], v) for k, v in st.items()
               if k.startswith('session_vars.')])
    session = botocore.session.Session(session_vars=sv)
    client = session.create_client('sqs')

    receive_params = {
        'MaxNumberOfMessages': int(st['max_number_of_messages']),
        'VisibilityTimeout': int(st['visibility_timeout']),
        'WaitTimeSeconds': int(st['wait_time_seconds']),
    }
    return BotoCoreTransport(queue_name, client, receive_params)
