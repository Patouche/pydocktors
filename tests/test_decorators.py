# -*- coding: utf-8 -*-
import unittest


def dec_func(name):
    return 'Hello %s' % name


class TestDocker(unittest.TestCase):
    """Test docker decorators"""

    @unittest.skip('TODO')
    def test_docker(self):
        # GIVEN

        # WHEN

        # THEN
        self.fail()


if __name__ == '__main__':
    unittest.main()
