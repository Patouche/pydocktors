# -*- coding: utf-8 -*-
import socket
import unittest

import docker
import mock
import signal

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

    @unittest.skip('TODO')
    def test_start(self):
        self.fail()

    @unittest.skip('TODO')
    def test_shutdown(self):
        self.fail()

    def test__wait_for_log_with_log_specified(self):
        # GIVEN
        docker_container = DockerContainer(
            image='alpine',
            wait_for_log='wait for log',
        )

        docker_container._container = mock.MagicMock()
        docker_container._container.logs.return_value = [
            'wait once',
            'wait twice with : "wait for log" present !!'
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

        socket_mock.return_value.connect_ex.side_effect = [0, 0, 1]

        # WHEN
        docker_container._wait_for_port()

        # THEN
        time_sleep_mock.assert_called()
        socket_mock.assert_called_with(socket.AF_INET, socket.SOCK_STREAM)
        socket_mock.return_value.connect_ex.assert_called_with(('127.0.0.1', 1234))
        self.assertEqual(socket_mock.return_value.connect_ex.call_count, 3, 'Should have been called 3 times')


if __name__ == '__main__':
    unittest.main()
