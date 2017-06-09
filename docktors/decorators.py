# -*- coding: utf-8 -*-
import logging
from docktors.core import decorated
from docktors.wdocker import DockerContainer

logger = logging.getLogger(__name__)


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
            return decorated(docker_container, func)

        return decorator

    return decorated(docker_container, func)
