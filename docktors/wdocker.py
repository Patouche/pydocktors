# -*- coding: utf-8 -*-
import docker
import logging

from .core import DecWrapper, DwArg

logger = logging.getLogger(__name__)


class DockerContainer(DecWrapper):
    """
    Docker container class. This class will start a new container and shutdown it.


    """
    container = None
    _props = {
        'image': DwArg(argtype=str, mandatory=True),
        'command': DwArg(argtype=str),
        'ports': DwArg(
            argtype=dict, default=dict(),
            alternatives=[
                ([(int, int)], lambda (v): dict(i for i in v))
            ]
        ),
        'environment': DwArg(
            argtype=dict, default=dict(),
            alternatives=[
                ([(str, str)], lambda (v): dict(i for i in v))
            ]
        ),
        'wait_for_log': DwArg(argtype=str),
        'wait_for_port': DwArg(argtype=int),
        'kill_signal': DwArg(argtype=int),
    }

    def __init__(self, **kwargs):
        """
        Class constructor to start and shutdown a container.
        """
        super(self.__class__, self).__init__(name='docker', inputs=kwargs, props=self._props)
        self._client = docker.from_env()

    def start(self):
        """
        Start a containers and wait for it.
        """
        image = self.p('image')
        logger.debug('[%s] image is starting ...', image)

        self.container = self._client.containers.run(
            image=image,
            detach=True,
            command=self.p('command'),
            ports=self.p('ports'),
            environment=self.p('environment'),
        )

        logger.debug('[%s] container start with id : %s', image, self.container.id)
        self._wait_for_log()

        logger.debug('[%s] container is ready (id=%s)', image, self.container.id)
        return self.container

    def shutdown(self):
        """
        Shutdown the container when exiting the decorator.
        """
        img = self.p('image')
        kill_signal = self.p('kill_signal')
        cid = self.container.id
        try:
            if self.container.status in ['running', 'created']:
                if kill_signal:
                    logger.debug('[%s] Shutdown (kill signal=%d) container with id : %s', img, kill_signal, cid)
                    self.container.kill(signal=kill_signal)
                else:
                    logger.debug('[%s] Trying to shutdown gracefully container with id : %s', img, cid)
                    self.container.stop(timeout=10)
        except Exception as e:
            raise RuntimeError('[%s] Unable to stop container %s ' % (img, cid), e)

    def _wait_for_log(self):
        wait_log = self.p('wait_for_log')
        if wait_log:
            for docker_log in self.container.logs(stream=True):
                docker_log = docker_log.rstrip()
                logger.debug('[%s - log][%s]', self.p('image'), docker_log)
                if wait_log in docker_log:
                    break
