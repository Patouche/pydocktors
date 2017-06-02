# -*- coding: utf-8 -*-
import logging
import functools

from .core import DockerContainer

logger = logging.getLogger(__name__)


def docker(func=None, **kwargs):
    """
    Decorator to startup and shutdown a docker container.

    :param func: the function to be decorated
    :param kwargs: parameters for docker containers
    :return: the decorated function
    """
    docker_container = DockerContainer(**kwargs)

    def decorated(func):

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            logger.debug('Starting container before test : %s', func.__name__)
            docker_container.start()
            try:
                logger.debug('Running test : %s', func.__name__)
                return func(*args, **kwargs)
            finally:
                logger.debug('Shutdown container in test : %s', func.__name__)
                docker_container.shutdown()

        return wrapper

    # Variable assigment : function is undefined
    if func is None:
        def decorator(func):
            return decorated(func)

        return decorator

    return decorated(func)
