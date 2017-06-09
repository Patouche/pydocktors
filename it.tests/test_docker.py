import unittest
import docker
import logging
import signal

import docktors

logging.basicConfig(format='%(asctime)-15s %(clientip)s %(user)-8s %(message)s', level=logging.DEBUG)

alpine_container = docktors.docker(
    image='alpine',
    command='sh'
)


@alpine_container
def hello(param):
    return "Hello %s" % param


@alpine_container
def alpine(func):
    return func()


@docktors.docker(
    inject_arg=True,
    image='mysql',
    ports={
        '3306/tcp': 3306
    },
    environment={
        'MYSQL_ROOT_PASSWORD': 'root',
        'MYSQL_USER': 'user',
        'MYSQL_PASSWORD': 'pwd',
        'MYSQL_DATABASE': 'testdb'
    },
    wait_for_log='mysqld: ready for connections',
    kill_signal=signal.SIGKILL,
)
def mysql_container_for_log(container, func):
    return func(container)


@docktors.docker(
    inject_arg=True,
    image='mysql',
    ports={
        '3306/tcp': 3306
    },
    environment={
        'MYSQL_ROOT_PASSWORD': 'root',
        'MYSQL_USER': 'user',
        'MYSQL_PASSWORD': 'pwd',
        'MYSQL_DATABASE': 'testdb'
    },
    wait_for_port=3306,
    kill_signal=signal.SIGKILL,
)
def mysql_container_for_port(container, func):
    return func(container)


class DockerTest(unittest.TestCase):
    def setUp(self):
        client = docker.from_env()
        for container in client.containers.list():
            container.kill(signal=signal.SIGKILL)

    def tearDown(self):
        client = docker.from_env()
        containers = client.containers.list()
        ids = [container.id for container in containers]
        self.assertEqual(msg='No containers should run. Found : %s' % ids, first=len(ids), second=0)

    def test_hello_world(self):
        # WHEN
        output = hello('World')

        # THEN
        self.assertEqual(msg='Should be equals', first=output, second='Hello World')

    def test_container_exist(self):
        # GIVEN
        def _is_alpine_up():
            containers = docker.from_env().containers.list()
            if len(containers) != 1:
                return False
            container = containers[0]
            return container.status == 'running' and container.attrs['Config']['Image'] == 'alpine'

        # WHEN
        output = alpine(_is_alpine_up)

        # THEN
        self.assertTrue(output, 'Container "mysql" should be up and running')

    def test_container_wait_for_log(self):
        # GIVEN
        def _mysql_query(container):
            return container is not None

        # WHEN
        output = mysql_container_for_log(_mysql_query)

        # THEN
        self.assertTrue(output, 'Should wait until log is in outputs')

    def test_container_wait_for_port(self):
        # GIVEN
        def _mysql_query(container):
            return container is not None

        # WHEN
        output = mysql_container_for_port(_mysql_query)

        # THEN
        self.assertTrue(output, 'Should wait until port is open')

    def test_container_injection_at_first(self):
        # GIVEN
        def _mysql_query(container):
            return container is not None

        # WHEN
        output = mysql_container_for_log(_mysql_query)

        # THEN
        self.assertTrue(output, 'Check container has been injected')


if __name__ == '__main__':
    unittest.main()
