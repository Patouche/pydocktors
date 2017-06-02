import unittest
import logging

import sys

import signal

import docktors

logging.basicConfig(format='%(asctime)-15s %(clientip)s %(user)-8s %(message)s', level=logging.DEBUG)


mysql_container = docktors.docker(
    image='mysql',
    bindings=[(3306, 3306)],
    wait_for_logs='mysqld: ready for connections',
    wait_for_port=[3306],
    signal=signal.SIGKILL,
)

@mysql_container
def hello(param):
    return "Hello %s" % param

@mysql_container
def mysql(func):
    return func()


class DockerTest(unittest.TestCase):

    def test_hello_world(self):
        # WHEN
        output = hello("World")

        # THEN
        self.assertEqual(msg="Should be equals", first=output, second="Hello World")
        # TODO : Check that there is not more running container (in tearDown)

    def test_mysql_connect(self):
        # GIVEN
        def _is_mysql_up():
            # TODO

        # WHEN
        output = mysql(_is_mysql_up)

        # THEN
        self.assertTrue(output, "Mysql should be up and running")


if __name__ == '__main__':
    unittest.main()
