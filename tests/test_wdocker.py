# -*- coding: utf-8 -*-
import signal
import socket
import unittest

import mock

from docktors.wdocker import DockerContainer


class TestDockerContainer(unittest.TestCase):
    """Testing class for DockerContainer"""

    def test_init(self):
        # GIVEN
        inputs = {
            'image': 'alpine',
            'command': 'sh',
            'ports': {
                '80/tcp': 80,
                '8888/tcp': 8888,
            },
            'volumes': {
                '/toto-1': {'bind': '/tata-1', 'mode': 'ro'},
                '/toto-2': {'bind': '/tata-2', 'mode': 'ro'},
            },
            'environment': {
                'ENV_VAR_1': 'val-1',
                'ENV_VAR_2': 'val-2',
            },
            'wait_for_log': 'wait for log',
            'wait_for_port': 80,
            'kill_signal': signal.SIGKILL,
        }

        # WHEN
        wrapper = DockerContainer(**inputs)

        # THEN
        [self.assertIsNotNone(wrapper.p(key), 'Key %s should be defined' % key) for key in inputs.keys()]

    def test_init_using_alternatives(self):
        # GIVEN
        inputs = {
            'image': 'alpine',
            'command': 'sh',
            'ports': [
                (80, 80),
                (8888, 8888),
            ],
            'volumes': [
                ('/toto-1', '/tata-1', 'ro'),
                ('/toto-2', '/tata-2', 'rw'),
            ],
            'environment': [
                ('ENV_VAR_1', 'val-1'),
                ('ENV_VAR_2', 'val-2'),
            ],
            'wait_for_log': 'wait for log',
            'wait_for_port': 80,
            'kill_signal': signal.SIGKILL,
        }

        # WHEN
        wrapper = DockerContainer(**inputs)

        # THEN
        [self.assertIsNotNone(wrapper.p(key), 'Key %s should be defined' % key) for key in inputs.keys()]

    @mock.patch(target='docker.from_env')
    def test_start(self, docker_mock):
        # GIVEN
        docker_container = DockerContainer(
            image='alpine',
            command='sh',
            ports=[
                (80, 80),
                (8888, 8888),
            ],
            volumes=[
                ('/toto-1', '/tata-1', 'ro'),
                ('/toto-2', '/tata-2', 'rw'),
            ],
            environment=[
                ('ENV_VAR_1', 'val-1'),
                ('ENV_VAR_2', 'val-2'),
            ],
        )

        # WHEN
        docker_container.start()

        # THEN
        docker_mock.assert_called_once_with()
        docker_mock.return_value.containers.run.assert_called_once_with(
            image='alpine',
            command='sh',
            detach=True,
            environment={'ENV_VAR_2': 'val-2', 'ENV_VAR_1': 'val-1'},
            ports={80: 80, 8888: 8888},
            volumes={
                '/toto-2': {'bind': '/tata-2', 'mode': 'rw'},
                '/toto-1': {'bind': '/tata-1', 'mode': 'ro'}
            }
        )
        self.assertEqual(docker_container._client, docker_mock.return_value, 'Docker client should be defined')
        self.assertEqual(
            docker_container._container,
            docker_mock.return_value.containers.run.return_value,
            "Docker container should have been defined from API's call returns"
        )

    def test_shutdown_bad_status(self):
        # GIVEN
        docker_container = DockerContainer(
            image='alpine'
        )
        container = mock.MagicMock()
        container.status = 'stopped'
        container.id = '55ee6c79294fa2304da51631b435940d78b0e31c56704159ed9644bfea10c86c'
        docker_container._container = container

        # WHEN
        docker_container.shutdown()

        # THEN
        docker_container._container.stop.assert_not_called()
        docker_container._container.kill.assert_not_called()

    def test_shutdown_stop_command(self):
        # GIVEN
        docker_container = DockerContainer(
            image='alpine'
        )
        container = mock.MagicMock()
        container.status = 'running'
        container.id = '55ee6c79294fa2304da51631b435940d78b0e31c56704159ed9644bfea10c86c'
        docker_container._container = container

        # WHEN
        docker_container.shutdown()

        # THEN
        docker_container._container.stop.assert_called_once_with(timeout=10)

    def test_shutdown_kill_command(self):
        # GIVEN
        docker_container = DockerContainer(
            image='alpine',
            kill_signal=signal.SIGKILL,
        )
        container = mock.MagicMock()
        container.status = 'running'
        container.id = '55ee6c79294fa2304da51631b435940d78b0e31c56704159ed9644bfea10c86c'
        docker_container._container = container

        # WHEN
        docker_container.shutdown()

        # THEN
        docker_container._container.kill.assert_called_once_with(signal=signal.SIGKILL)

    def test__wait_for_log_with_log_specified(self):
        # GIVEN
        docker_container = DockerContainer(
            image='alpine',
            wait_for_log='wait for log',
        )

        docker_container._container = mock.MagicMock()
        docker_container._container.logs.return_value = [
            b'wait once',
            b'wait twice with : "wait for log" present !!'
        ]

        # WHEN
        docker_container._wait_for_log()

        # THEN
        docker_container._container.logs.assert_called_once_with(stream=True)

    def test__wait_for_log_without_log_specified(self):
        # GIVEN
        docker_container = DockerContainer(
            image='alpine',
        )

        docker_container._container = mock.MagicMock()

        # WHEN
        docker_container._wait_for_log()

        # THEN
        docker_container._container.logs.assert_not_called()

    @mock.patch(target='socket.socket')
    @mock.patch(target='time.sleep')
    def test__wait_for_port_with_port_specified(self, time_sleep_mock, socket_mock):
        # GIVEN
        docker_container = DockerContainer(
            image='alpine',
            wait_for_port=1234,
        )

        docker_container._client = mock.MagicMock()
        docker_container._client.containers.get.return_value.attrs = dict(
            NetworkSettings=dict(IPAddress='172.10.0.2')
        )
        docker_container._container = mock.MagicMock(id='c5f0cad13259')

        socket_mock.return_value.connect_ex.side_effect = [1, 1, 0]

        # WHEN
        docker_container._wait_for_port()

        # THEN
        time_sleep_mock.assert_called()
        socket_mock.assert_called_with(socket.AF_INET, socket.SOCK_STREAM)
        connect_ex_mock = socket_mock.return_value.connect_ex
        connect_ex_mock.assert_called_with(('172.10.0.2', 1234))
        self.assertEqual(connect_ex_mock.call_count, 3, 'Should have been called 3 times instead of {call_nb}'.format(
            call_nb=connect_ex_mock.call_count
        ))


if __name__ == '__main__':
    unittest.main()
