# -*- coding: utf-8 -*-

from . import applications, interfaces, orbiter, transports, workers


__version__ = '0.1'
default_config = {
    'transport_factory': 'sqs_consumer.transports.botocore_factory',
    'transport.botocore.max_number_of_messages': '1',
    # 'transport.botocore.queue_name': '',
    # 'transport.botocore.session_vars.profile': '',
    # 'transport.botocore.session_vars.config_file': '',
    # 'transport.botocore.session_vars.credentials_file': '',
    'transport.botocore.visibility_timeout': '0',
    'transport.botocore.wait_time_seconds': '20',
    'worker_factory': 'sqs_consumer.workers.sync_factory',
}


def server_runner(app, global_config, **settings):
    """
    :param app: callable
    :param global_config: dict
    :param settings: dict
    :return: int
    """
    config = default_config.copy()
    config.update(global_config)
    config.update(settings)
    server = orbiter.factory(app, config)
    server.serve_forever()
    return server.retval
