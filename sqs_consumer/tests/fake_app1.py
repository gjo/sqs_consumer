# -*- coding: utf-8 -*-

from ..applications import DictDispatch, dict_dispatch_task


@dict_dispatch_task('value')
def test(data):
    """
    :type data: dict
    :rtype: bool
    """
    return bool(data.get('return_value'))


def main(global_config, **settings):
    app = DictDispatch('key')
    app.scan()
    return app
