# -*- coding: utf-8 -*-

import unittest
import mock


class ServerRunnerTestCase(unittest.TestCase):

    @mock.patch('sqs_consumer.orbiter.Orbiter.serve_forever')
    def test(self, mocked):
        from .. import server_runner
        from ..testing import IApplicationMock
        app = IApplicationMock()
        server_runner(app, {
            'transport_factory': 'sqs_consumer.testing.transport_mock_factory',
            'worker_factory': 'sqs_consumer.testing.worker_mock_factory',
        })
