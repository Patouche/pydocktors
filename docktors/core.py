# -*- coding: utf-8 -*-
import docker
import logging

logger = logging.getLogger(__name__)


class DockerArgs(object):
    """
    Docker Args class for parsing input args of decorator.
    """

    def __init__(self, inputs, props):
        self._inputs = inputs
        self._props = props

    def test(self):
        """
        Test input arguments

        TODO : This should throw exceptions.
        """
        return self._inputs


class DockerContainer(object):
    """
    Docker container class. This class will start a new container and shutdown it.


    """
    _container = None
    _props = {
        'image': (str, True),
        'bindings': ([(str, str)], True),
        'wait_for_logs': ([str], False),
        'wait_for_port': ([list], False),
        'signal': (int, False),
    }

    def __init__(self, **kwargs):
        """
        Class constructor to start and shutdown a container.
        """
        params = DockerArgs(kwargs, self._props).test()
        self._client = docker.from_env()
        self._image = params.get('image', 'mysql')
        self._wait_log = params.get('wait_for_log')

    def start(self):
        """
        Start a containers and wait for it.
        """
        logger.debug('[%s] image is starting ...', self._image)

        self._container = self._client.containers.run(
            image=self._image,
            detach=True,
            environment={
                'MYSQL_ROOT_PASSWORD': 'test'
            },
        )

        logger.debug('[%s] container start with id : %s', self._image, self._container.id)
        self._wait_for_log()

        logger.debug('[%s] container is ready (id=%s)', self._image, self._container.id)
        return self._container

    def shutdown(self):
        """
        Shutdown the container when exiting the decorator.
        """
        try:
            logger.debug('[%s] Stopping container with id : %s', self._image, self._container.id)
            self._container.stop(timeout=5)
        except Exception as e:
            raise RuntimeError('[%s] Unable to stop container %s ' % (self._image, self._container.id), e)

    def _wait_for_log(self):
        if self._wait_log:
            for docker_log in self._container.logs(stream=True):
                docker_log = docker_log.rstrip()
                logger.debug('[%s - log][%s]', self._image, docker_log)
                if self._wait_log in docker_log:
                    break
