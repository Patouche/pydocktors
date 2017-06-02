# -*- coding: utf-8 -*-
import logging
import functools

from .wdocker import DockerContainer

logger = logging.getLogger(__name__)


def _decorated(wrapping, func):

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger.debug('Starting %s before function : %s', wrapping.__class__, func.__name__)
        wrapping.start()
        try:
            logger.debug('Executing function : %s', func.__name__)
            func_args = tuple([wrapping]) + args if wrapping.inject_arg else args
            return func(*func_args, **kwargs)
        except Exception as e:
            logger.error('Error in decorator : %s', e.message)
            raise e
        finally:
            logger.debug('Shutdown %s before function : %s', wrapping.__class__, func.__name__)
            wrapping.shutdown()

    return wrapper


def docker(func=None, **kwargs):
    """
    Decorator to startup and shutdown a docker container.

    :param func: the function to be decorated
    :param kwargs: parameters for docker containers
    :return: the decorated function
    """
    docker_container = DockerContainer(**kwargs)

    # Decorator in variable assignment : function is undefined
    if func is None:
        def decorator(func):
            return _decorated(docker_container, func)

        return decorator

    return _decorated(docker_container, func)
