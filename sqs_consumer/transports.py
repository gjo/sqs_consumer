# -*- coding: utf-8 -*-

import logging
import botocore
import botocore.session
from zope.interface import implementer
from .interfaces import IMessage, ITransport


logger = logging.getLogger(__name__)


@implementer(IMessage)
class SQSMessage(object):

    def __init__(self, transport, data):
        """
        :type transport: SQSTransport
        :type data: dict[str, bytes]
        """
        self.transport = transport
        self.data = data

    # :type: bytes
    id = property(lambda self: self.data['MessageId'])

    # :type: bytes
    body = property(lambda self: self.data['Body'])

    def delete(self):
        self.transport.delete_message(self.data)


@implementer(ITransport)
class SQSTransport(object):

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
        :rtype: collections.Iterable[SQSMessage]
        """
        ret = self.receive_message()
        if 'Messages' in ret:
            logger.info('Polled: %d messages', len(ret['Messages']))
            for m in ret['Messages']:
                yield SQSMessage(self, m)
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
        :type message: SQSMessage
        :rtype: dict
        """
        params = dict(QueueUrl=self.queue_url,
                      ReceiptHandle=message['ReceiptHandle'])
        logger.debug('[PROTO] DeleteMessage Call: %r', params)
        ret = self.client.delete_message(**params)
        logger.debug('[PROTO] DeleteMessage Return: %r', ret)
        return ret


def sqs_factory(settings, prefix='transport.sqs.'):
    """
    :type settings: dict
    :type prefix: str
    :rtype: SQSTransport
    """
    st = dict([(k[len(prefix):], v) for k, v in settings.items()
               if k.startswith(prefix)])

    queue_name = st['queue_name']

    sv = dict([(k[len('botocore.'):], v) for k, v in st.items()
               if k.startswith('botocore.')])
    session = botocore.session.Session(session_vars=sv)
    client = session.create_client('sqs')

    receive_params = {
        'MaxNumberOfMessages': int(st['max_number_of_messages']),
        'VisibilityTimeout': int(st['visibility_timeout']),
        'WaitTimeSeconds': int(st['wait_time_seconds']),
    }
    return SQSTransport(queue_name, client, receive_params)
