# -*- coding: utf-8 -*-

import unittest
import mock
from zope.interface.verify import verifyClass, verifyObject


class BotoCoreMessageTestCase(unittest.TestCase):

    def test_interface(self):
        from ..interfaces import IMessage
        from ..testing import ITransportMock, dummy_sqs_message
        from ..transports import BotoCoreMessage
        verifyClass(IMessage, BotoCoreMessage)
        obj = BotoCoreMessage(ITransportMock(), dummy_sqs_message())
        verifyObject(IMessage, obj)

    def test_props(self):
        from ..testing import ITransportMock, dummy_sqs_message
        from ..transports import BotoCoreMessage
        obj = BotoCoreMessage(ITransportMock(), dummy_sqs_message())
        self.assertEqual(obj.id, '__dummy_id__')
        self.assertEqual(obj.body, '__dummy_body__')

    def test_delete(self):
        from ..testing import ITransportMock, dummy_sqs_message
        from ..transports import BotoCoreMessage
        transport = ITransportMock()
        msg = dummy_sqs_message()
        obj = BotoCoreMessage(transport, msg)
        transport.delete_message = mock.Mock()
        obj.delete()
        transport.delete_message.assert_called_once_with(msg)


class BotoCoreTransportTestCase(unittest.TestCase):

    def test_interface(self):
        from ..interfaces import ITransport
        from ..testing import sqs_client_mock
        from ..transports import BotoCoreTransport
        client = sqs_client_mock()
        verifyClass(ITransport, BotoCoreTransport)
        obj = BotoCoreTransport('__qname__', client, {'k': 'v'})
        verifyObject(ITransport, obj)

    def test_call_0(self):
        from ..testing import sqs_client_mock
        from ..transports import BotoCoreTransport
        client = sqs_client_mock()
        obj = BotoCoreTransport('__qname__', client, {'k': 'v'})
        obj.receive_message = mock.Mock(return_value={})
        ret = list(obj())
        self.assertEqual(len(ret), 0)
        obj.receive_message.assert_called_once_with()

    def test_call_1(self):
        from ..testing import sqs_client_mock, dummy_sqs_message
        from ..transports import BotoCoreMessage, BotoCoreTransport
        client = sqs_client_mock()
        obj = BotoCoreTransport('__qname__', client, {'k': 'v'})
        obj.receive_message = mock.Mock(return_value={
            'Messages': [dummy_sqs_message()],
        })
        ret = list(obj())
        self.assertEqual(len(ret), 1)
        self.assertIsInstance(ret[0], BotoCoreMessage)
        obj.receive_message.assert_called_once_with()

    def test_call_2(self):
        from ..testing import sqs_client_mock, dummy_sqs_message
        from ..transports import BotoCoreMessage, BotoCoreTransport
        client = sqs_client_mock()
        obj = BotoCoreTransport('__qname__', client, {'k': 'v'})
        obj.receive_message = mock.Mock(return_value={
            'Messages': [dummy_sqs_message(), dummy_sqs_message()],
        })
        ret = list(obj())
        self.assertEqual(len(ret), 2)
        self.assertIsInstance(ret[0], BotoCoreMessage)
        self.assertIsInstance(ret[1], BotoCoreMessage)
        self.assertIsNot(ret[0], ret[1])
        obj.receive_message.assert_called_once_with()

    def test_get_queue_url(self):
        from ..testing import sqs_client_mock
        from ..transports import BotoCoreTransport
        client = sqs_client_mock()
        obj = BotoCoreTransport('__qname__', client, {'k': 'v'})
        self.assertEqual(obj.queue_url, '__dummy_url__')

    def test_receive_message(self):
        from ..testing import sqs_client_mock
        from ..transports import BotoCoreTransport
        client = sqs_client_mock()
        obj = BotoCoreTransport('__qname__', client, {'k': 'v'})
        self.assertIs(obj.receive_message(),
                      client.receive_message.return_value)
        client.receive_message.assert_called_once_with(
            QueueUrl='__dummy_url__',
            k='v',
        )

    def test_delete_message(self):
        from ..testing import IMessageMock, sqs_client_mock
        from ..transports import BotoCoreTransport
        client = sqs_client_mock()
        obj = BotoCoreTransport('__qname__', client, {'k': 'v'})
        msg = IMessageMock()
        self.assertIs(obj.delete_message(msg),
                      client.delete_message.return_value)
        client.delete_message.assert_called_once_with(
            QueueUrl='__dummy_url__',
            ReceiptHandle=msg.receipt_handle,
        )


class BotoCoreFactoryTestCase(unittest.TestCase):

    @mock.patch('sqs_consumer.transports.BotoCoreTransport.get_queue_url')
    def test(self, mocked):
        from ..transports import botocore_factory
        ret = botocore_factory({
            'testing.queue_name': '__queue_name__',
            'testing.max_number_of_messages': '0',
            'testing.visibility_timeout': '1',
            'testing.wait_time_seconds': '2',
        }, prefix='testing.')
        self.assertEqual(ret.queue_name, '__queue_name__')
        self.assertDictEqual(ret.receive_params, {
            'MaxNumberOfMessages': 0,
            'VisibilityTimeout': 1,
            'WaitTimeSeconds': 2,
        })
