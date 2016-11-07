# -*- coding: utf-8 -*-

import unittest
from zope.interface.verify import verifyClass, verifyObject


class SyncWorkerTestCase(unittest.TestCase):

    def test_interface(self):
        from ..interfaces import IWorker
        from ..testing import IApplicationMock
        from ..workers import SyncWorker
        verifyClass(IWorker, SyncWorker)
        verifyObject(IWorker, SyncWorker(IApplicationMock()))

    def test_invoke_true(self):
        from ..testing import IApplicationMock, IMessageMock
        from ..workers import sync_factory
        app = IApplicationMock()
        msg = IMessageMock()
        obj = sync_factory(app, {})

        app.return_value = True
        obj.invoke(msg)
        app.assert_called_once_with(msg.body)
        msg.delete.assert_called_once_with()

    def test_invoke_false(self):
        from ..testing import IApplicationMock, IMessageMock
        from ..workers import sync_factory
        app = IApplicationMock()
        msg = IMessageMock()
        obj = sync_factory(app, {})

        app.return_value = False
        obj.invoke(msg)
        app.assert_called_once_with(msg.body)
        msg.delete.assert_not_called()

    def test_invoke_raise(self):
        from ..testing import IApplicationMock, IMessageMock
        from ..workers import sync_factory
        app = IApplicationMock()
        msg = IMessageMock()
        obj = sync_factory(app, {})

        app.side_effect = Exception
        obj.invoke(msg)
        app.assert_called_once_with(msg.body)
        msg.delete.assert_not_called()
