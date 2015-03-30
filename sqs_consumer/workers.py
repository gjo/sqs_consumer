# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import logging
import signal
import botocore.session
from pyramid.settings import asbool


logger = logging.getLogger(__name__)
marker = object()


class Worker(object):

    app = None  # :type: callable
    queue_name = None  # :type: str
    protocol_dump = None  # :type: bool

    max_number_of_messages = marker  # :type: int
    visibility_timeout = marker  # :type: int
    wait_time_seconds = marker  # :type: int

    profile = marker  # :type: str
    credentials_file = marker  # :type: str
    config_file = marker  # :type: str
    metadata_service_num_attempts = marker  # :type: int
    provider = marker  # :type: str
    region = marker  # :type: str
    data_path = marker  # :type: str
    metadata_service_timeout = marker  # :type: int

    client = None  # :type: botocore.client.sqs
    logger = logger
    stop = None  # :type: bool
    queue_url = None  # :type: str
    session = None  # :type: botocore.session.Session

    def __init__(self, **kwargs):
        for k in kwargs:
            if hasattr(self, k):
                setattr(self, k, kwargs[k])
        self.stop = False

    def prepare(self):
        signal.signal(signal.SIGINT, self.handle_stop)
        signal.signal(signal.SIGQUIT, self.handle_stop)
        signal.signal(signal.SIGTERM, self.handle_stop)
        params = dict()
        if self.profile is not marker:
            params['profile'] = self.profile
        if self.credentials_file is not marker:
            params['credentials_file'] = self.credentials_file
        if self.config_file is not marker:
            params['config_file'] = self.config_file
        if self.metadata_service_num_attempts is not marker:
            params['metadata_service_num_attempts'] = \
                self.metadata_service_num_attempts
        if self.provider is not marker:
            params['provider'] = self.provider
        if self.region is not marker:
            params['region'] = self.region
        if self.data_path is not marker:
            params['data_path'] = self.data_path
        if self.metadata_service_timeout is not marker:
            params['metadata_service_timeout'] = self.metadata_service_timeout
        self.session = botocore.session.get_session(params)
        self.client = self.session.create_client('sqs')
        self.queue_url = self.get_queue_url()

    def handle_stop(self, sig, frame):
        self.logger.info('Received signal %r', sig)
        self.stop = True

    def serve_forever(self):
        self.prepare()
        self.logger.info('Start polling to %s', self.queue_name)
        while not self.stop:
            self.serve_oneshot()
        self.logger.info('Finish polling to %s', self.queue_name)

    def serve_oneshot(self):
        recv_ret = self.receive_messages()
        if 'Messages' in recv_ret:
            self.logger.debug('Polled: %d messages', len(recv_ret['Messages']))
            for message in recv_ret['Messages']:
                message_id = message['MessageId']
                self.logger.info('Process Message: %s', message_id)
                body = message['Body']
                self.logger.debug('Message Body: %r', body)
                app_ret = None
                try:
                    app_ret = self.app(body)
                except:
                    self.logger.exception('Consumer Halted')
                if app_ret:
                    self.logger.info('Delete Message: %s', message_id)
                    self.delete_message(message)
        else:
            # self.logger.debug('Polled: no messages')
            pass

    def get_queue_url(self):
        params = dict(QueueName=self.queue_name)
        if self.protocol_dump:
            self.logger.debug('[PROTO] GetQueueUrl Call: %r', params)
        ret = self.client.get_queue_url(**params)
        if self.protocol_dump:
            self.logger.debug('[PROTO] GetQueueUrl Return: %r', ret)
        return ret['QueueUrl']

    def receive_messages(self):
        params = dict(QueueUrl=self.queue_url)
        if self.max_number_of_messages is not marker:
            params['MaxNumberOfMessages'] = self.max_number_of_messages
        if self.visibility_timeout is not marker:
            params['VisibilityTimeout'] = self.visibility_timeout
        if self.wait_time_seconds is not marker:
            params['WaitTimeSeconds'] = self.wait_time_seconds
        # AttributeNames=[],
        # MessageAttributeNames=[],
        if self.protocol_dump:
            self.logger.debug('[PROTO] ReceiveMessage Call: %r', params)
        ret = self.client.receive_message(**params)
        if self.protocol_dump:
            self.logger.debug('[PROTO] ReceiveMessage Return: %r', ret)
        return ret

    def delete_message(self, message):
        params = dict(QueueUrl=self.queue_url,
                      ReceiptHandle=message['ReceiptHandle'])
        if self.protocol_dump:
            self.logger.debug('[PROTO] DeleteMessage Call: %r', params)
        ret = self.client.delete_message(**params)
        if self.protocol_dump:
            self.logger.debug('[PROTO] DeleteMessage Return: %r', ret)
        return ret


def run_pserve(app, global_config, **settings):
    """
    :param app: callable
    :param global_config: dict
    :param settings: dict
    :return: int
    """
    params = {
        'app': app,
        'queue_name': settings['queue_name'],
        'protocol_dump': asbool(settings.get('protocol_dump')),
    }
    for k in ('max_number_of_messages', 'visibility_timeout',
              'wait_time_seconds', 'metadata_service_num_attempts',
              'metadata_service_timeout'):
        if k in settings and len(settings[k]) > 0:
            params[k] = int(settings[k])
    for k in ('profile', 'credentials_file', 'config_file', 'provider',
              'region', 'data_path'):
        if k in settings and len(settings[k]) > 0:
            params[k] = settings[k]
    worker = Worker(**params)
    worker.serve_forever()
    return 0
