# -*- coding: utf-8 -*-
import unittest

import docktors
from .sample import mysql_main

mysql_docker = docktors.docker(
    inject_arg=True,
    image='mysql',
    wait_for_port=3306,
    ports=[
        (3306, 3306)
    ],
    environment=dict(
        MYSQL_ROOT_PASSWORD='container-pwd',
    )
)


class TestMain(unittest.TestCase):

    @mysql_docker
    def test_main(self, container):
        ip = container.attrs['NetworkSettings']['IPAddress']
        mysql_main(host=ip, password='container-pwd')


if __name__ == '__main__':
    unittest.main()
