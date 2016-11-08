# -*- coding: utf-8 -*-

import unittest
import mock
from zope.interface.verify import verifyClass, verifyObject


class SyncWorkerTestCase(unittest.TestCase):

    def test_interface(self):
        from ..interfaces import IWorker
        from ..testing import IApplicationMock
        from ..workers import SyncWorker
        verifyClass(IWorker, SyncWorker)
        verifyObject(IWorker, SyncWorker(IApplicationMock()))

    def test_invoke(self):
        from ..testing import IApplicationMock, IMessageMock
        from ..workers import sync_factory
        app = IApplicationMock()
        app.side_effect = [True, False, Exception]
        obj = sync_factory(app, {})
        msgs = [IMessageMock(), IMessageMock(), IMessageMock()]
        obj.invoke(msgs)
        app.assert_has_calls([
            mock.call(msgs[0].body),
            mock.call(msgs[1].body),
            mock.call(msgs[2].body),
        ])
        msgs[0].delete.assert_called_once_with()
        msgs[1].delete.assert_not_called()
        msgs[2].delete.assert_not_called()
