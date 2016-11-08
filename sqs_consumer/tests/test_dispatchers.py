# -*- coding: utf-8 -*-

import unittest
from zope.interface.verify import verifyClass, verifyObject


class DictDispatchTestCase(unittest.TestCase):

    def test_interface(self):
        from ..applications import DictDispatch
        from ..interfaces import IApplication
        verifyClass(IApplication, DictDispatch)
        obj = DictDispatch('__testing_key__')
        verifyObject(IApplication, obj)

    def test_impl(self):
        from ..interfaces import IApplication
        from . import fake_app1

        app = fake_app1.main({})
        verifyObject(IApplication, app)

        message = r'{"key":"value","return_value":1}'
        self.assertTrue(app(message))
