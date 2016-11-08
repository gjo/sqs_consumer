# -*- coding: utf-8 -*-

import unittest
import mock


class OrbiterTestCase(unittest.TestCase):

    def test_init(self):
        from ..orbiter import Orbiter
        from ..testing import IApplicationMock, ITransportMock, IWorkerMock
        app = IApplicationMock()
        transport = ITransportMock()
        worker = IWorkerMock()
        obj = Orbiter(app, transport, worker)
        self.assertIs(obj.app, app)
        self.assertIs(obj.transport, transport)
        self.assertIs(obj.worker, worker)

    def test_handle_stop(self):
        from ..orbiter import Orbiter
        from ..testing import IApplicationMock, ITransportMock, IWorkerMock
        app = IApplicationMock()
        transport = ITransportMock()
        worker = IWorkerMock()
        obj = Orbiter(app, transport, worker)
        self.assertFalse(obj.stop)
        obj.handle_stop(mock.Mock(), mock.Mock())
        self.assertTrue(obj.stop)

    @mock.patch('sqs_consumer.orbiter.Orbiter.serve_oneshot')
    def test_serve_forever(self, mocked):
        from ..orbiter import Orbiter
        from ..testing import IApplicationMock, ITransportMock, IWorkerMock
        app = IApplicationMock()
        transport = ITransportMock()
        worker = IWorkerMock()
        obj = Orbiter(app, transport, worker)
        mocked.side_effect = lambda: setattr(obj, 'stop', True)
        obj.serve_forever()
        mocked.assert_called_once_with()

    def test_serve_oneshot(self):
        from ..orbiter import Orbiter
        from ..testing import IApplicationMock, ITransportMock, IWorkerMock
        app = IApplicationMock()
        transport = ITransportMock()
        worker = IWorkerMock()
        obj = Orbiter(app, transport, worker)
        obj.serve_oneshot()
        transport.assert_called_once_with()
        worker.invoke.assert_called_once_with(transport.return_value)


class FactoryTestCase(unittest.TestCase):

    def test(self):
        from ..orbiter import factory
        from ..testing import IApplicationMock
        app = IApplicationMock()
        ret = factory(app, {
            'transport_factory': 'sqs_consumer.testing.transport_mock_factory',
            'worker_factory': 'sqs_consumer.testing.worker_mock_factory',
        })
        self.assertIs(ret.app, app)
