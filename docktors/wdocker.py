# -*- coding: utf-8 -*-
import socket
import docker
import logging
import time
from .core import DecWrapper, DwArg

logger = logging.getLogger(__name__)

DOCKER_CONTAINER_PROPS = {
    'image': DwArg(argtype=str, mandatory=True),
    'command': DwArg(argtype=str),
    'ports': DwArg(
        argtype=dict,
        default=dict(),
        alternatives=[
            ([(int, int)], lambda v: dict(i for i in v))
        ]
    ),
    'volumes': DwArg(
        argtype=dict,
        default=dict(),
        alternatives=[
            ([(str, str, str)], lambda v: dict((i[0], {'bind': i[1], 'mode': i[2]}) for i in v))
        ]
    ),
    'environment': DwArg(
        argtype=dict,
        default=dict(),
        alternatives=[
            ([(str, str)], lambda v: dict(i for i in v))
        ]
    ),
    'wait_for_log': DwArg(argtype=str),
    'wait_for_port': DwArg(argtype=int),
    'kill_signal': DwArg(argtype=int),
}


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
        super(self.__class__, self).__init__(
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
        except Exception as e:
            raise RuntimeError('[%s] Unable to stop container %s ' % (img, cid), e)

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
        wait_port, image, result = self.p('wait_for_port'), self.p('image'), 0
        if wait_port:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            while result == 0:
                logger.debug('[%s] Waiting for port %d to respond', image, wait_port)
                result = sock.connect_ex(('127.0.0.1', wait_port))
                if result == 0:
                    time.sleep(1)
            logger.debug('[%s] Port %d is now responding', image, wait_port)
