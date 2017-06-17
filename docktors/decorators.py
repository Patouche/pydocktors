# -*- coding: utf-8 -*-
"""
Decorators module
"""
import logging
from docktors.core import decorated
from docktors.wdocker import DockerContainer

logger = logging.getLogger(__name__)


def docker(func=None, **kwargs):
    """
    Decorator to startup and shutdown a docker container.

    :param image: The name of the image to use.
    :param command: The input docker command to run,
    :param ports: The ports bindings to made
    :param volumes: The volumes to mount
    :param environment: The environment value
    :param wait_for_log: A string to wait in the logs before going into the function
    :param wait_for_port: A string to wait before going into the function
    :param kill_signal: If you want to kill the container, the signal to use. Otherwise, only a stop will be made.
    :param func: the function to be decorated
    :return: the decorated function
    """
    docker_container = DockerContainer(**kwargs)

    # Decorator in variable assignment : function is undefined
    if func is None:
        def decorator(func):  # pylint: disable=locally-disabled, missing-docstring
            return decorated(docker_container, func)

        return decorator

    return decorated(docker_container, func)
