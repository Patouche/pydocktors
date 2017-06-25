# -*- coding: utf-8 -*-
"""
WDocker module.

This module is design to define the wrapper to use in the generic decorator.
"""
import contextlib
import socket
import logging
import time
from errno import errorcode

import docker
from .core import DecWrapper

logger = logging.getLogger(__name__)

DOCKER_CONTAINER_PROPS = dict(
    image=dict(argtype=str, mandatory=True),
    command=dict(argtype=str),
    ports=dict(
        argtype=dict,
        default=dict(),
        alternatives=[
            ([(int, int)], lambda v: dict(i for i in v))
        ]
    ),
    volumes=dict(
        argtype=dict,
        default=dict(),
        alternatives=[
            ([(str, str, str)], lambda v: dict((i[0], {'bind': i[1], 'mode': i[2]}) for i in v))
        ]
    ),
    environment=dict(
        argtype=dict,
        default=dict(),
        alternatives=[
            ([(str, str)], lambda v: dict(i for i in v))
        ]
    ),
    wait_for_log=dict(argtype=str),
    wait_for_port=dict(argtype=int),
    kill_signal=dict(argtype=int),
)


class DockerContainer(DecWrapper):
    """
    Docker container class. This class will start a new container and shutdown it.
    """
    _client = None
    _container = None

    def __init__(self, **kwargs):
        """
        Class constructor to start and shutdown a container.
        """
        super(DockerContainer, self).__init__(
            name='docker',
            inputs=kwargs,
            props=DOCKER_CONTAINER_PROPS
        )

    def get_args(self):
        return [self._container]

    def start(self):
        """
        Start a containers and wait for it.
        """
        self._client = docker.from_env()

        image = self.p('image')
        logger.debug('[%s] image is starting ...', image)

        self._container = self._client.containers.run(
            image=image,
            detach=True,
            command=self.p('command'),
            volumes=self.p('volumes'),
            ports=self.p('ports'),
            environment=self.p('environment'),
        )

        logger.debug('[%s] container start with id : %s', image, self._container.id)
        self._wait_for_log()
        self._wait_for_port()
        logger.debug('[%s] container is ready (id=%s)', image, self._container.id)
        return self._container

    def shutdown(self):
        """
        Shutdown the container when exiting the decorator.
        """
        img = self.p('image')
        kill_signal = self.p('kill_signal')
        cid = self._container.id
        try:
            if self._container.status in ['running', 'created']:
                if kill_signal:
                    logger.debug('[%s] Shutdown (kill signal=%d) container with id : %s', img, kill_signal, cid)
                    self._container.kill(signal=kill_signal)
                else:
                    logger.debug('[%s] Trying to shutdown gracefully container with id : %s', img, cid)
                    self._container.stop(timeout=10)
        except Exception as ex:
            raise RuntimeError('[%s] Unable to stop container %s ' % (img, cid), ex)

    def _wait_for_log(self):
        wait_log, image = self.p('wait_for_log'), self.p('image')
        if wait_log:
            for docker_log in self._container.logs(stream=True):
                docker_log = docker_log.rstrip()
                logger.debug('[%s - log][%s]', image, docker_log)
                if wait_log in docker_log.decode('utf-8'):
                    break
            logger.debug('[%s] Log \'%s\' has been found in container logs', image, wait_log)

    def _wait_for_port(self):
        wait_port, image, res = self.p('wait_for_port'), self.p('image'), 1
        if wait_port:
            container_id = self._container.id
            container_info = self._client.containers.get(container_id)
            ip_address = container_info.attrs['NetworkSettings']['IPAddress']
            with contextlib.closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
                while res != 0:
                    res = sock.connect_ex((ip_address, wait_port))
                    logger.debug(
                        '[%s] Waiting for port %d to respond (code:%d => %s).',
                        image, wait_port, res, errorcode.get(res, '--')
                    )
                    time.sleep(0.1 if res != 0 else 0)
            logger.debug('[%s] Port %d is now responding.', image, wait_port)
