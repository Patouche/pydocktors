# -*- coding: utf-8 -*-
import unittest

import mock

from docktors.core import DecWrapper, decorated


class TestDecWrapper(unittest.TestCase):
    def test__check_inputs_mandatory_arg_missing(self):
        # GIVEN
        props = dict(str_prop=dict(argtype=[str], mandatory=True))
        inputs = dict(other_prop='value')

        # WHEN
        with self.assertRaises(SyntaxError) as cm:
            DecWrapper('Test', inputs, props)

        # THEN
        self.assertEqual(
            str(cm.exception),
            "[Test] : Mandatory option 'str_prop' is missing."
        )

    def test__check_inputs_prop_undefined(self):
        # GIVEN
        props = {'int_prop': dict(argtype=[int], default=1)}
        inputs = {'undefined_prop': 'toto'}

        # WHEN
        with self.assertRaises(SyntaxError) as cm:
            DecWrapper('Test', inputs, props)

        # THEN
        self.assertEqual(
            str(cm.exception),
            "[Test] : Option 'undefined_prop' doesn't not exist."
        )

    def test__check_inputs_bad_int_type(self):
        # GIVEN
        props = {'int_prop': dict(argtype=int, default=1)}
        inputs = {'int_prop': 'toto'}

        # WHEN
        with self.assertRaises(TypeError) as cm:
            DecWrapper('Test', inputs, props)

        # THEN
        self.assertEqual(
            str(cm.exception),
            "[Test] : Option 'int_prop' bad type. Expected 'int'. Got 'str' instead."
        )

    def test__check_inputs_ok_int_type(self):
        # GIVEN
        props = {'int_prop': dict(argtype=int, default=1)}
        inputs = {'int_prop': 5}

        # WHEN
        wrapper = DecWrapper('Test', inputs, props)

        # THEN
        self.assertEqual(wrapper.p('int_prop'), 5)

    def test__check_inputs_ok_int_type_alternative(self):
        # GIVEN
        props = {'int_prop': dict(argtype=int, default=1, alternatives=[(str, lambda i: int(i))])}
        inputs = {'int_prop': '5'}

        # WHEN
        wrapper = DecWrapper('test', inputs, props)

        # THEN
        self.assertEqual(wrapper.p('int_prop'), 5)

    def test__check_inputs_ok_tuple_list_type(self):
        # GIVEN
        props = {'tuple_list_prop': dict(argtype=[(int, str)], default=list())}
        inputs = {'tuple_list_prop': [(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')]}

        # WHEN
        wrapper = DecWrapper('Test', inputs, props)

        # THEN
        self.assertEqual(wrapper.p('tuple_list_prop'), [(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')])

    def test__check_inputs_bad_dict_using_alternative(self):
        # GIVEN
        props = {
            'dict_prop': dict(argtype=dict, alternatives=[([(int, int)], lambda x: x)], default=dict())
        }
        inputs = {
            'dict_prop': [
                ('10', '15'),
                ('20', '30'),
            ]
        }

        # WHEN
        with self.assertRaises(TypeError) as cm:
            DecWrapper('Test', inputs, props)

        # THEN
        self.assertEqual(
            str(cm.exception),
            "[Test] : Option 'dict_prop' bad type. Expected 'dict'. Got 'list' instead."
        )

    def test__check_inputs_ok_dict_using_alternative(self):
        # GIVEN
        props = {
            'dict_prop': dict(
                argtype=dict,
                alternatives=[
                    ([(int, int)], lambda v: dict(i for i in v))
                ],
                default=dict()
            )
        }
        inputs = {'dict_prop': [(10, 15), (20, 30)]}

        # WHEN
        wrapper = DecWrapper('Test', inputs, props)

        # THEN
        self.assertEqual(wrapper.p('dict_prop'), {10: 15, 20: 30})

    def test__check_inputs_set_defaults(self):
        # GIVEN
        props = {'int_prop': dict(argtype=[int], default=1)}
        inputs = {}

        # WHEN
        wrapper = DecWrapper('Test', inputs, props)

        # THEN
        self.assertEqual(wrapper.p('int_prop'), 1)


def dec_function(name):
    return 'Hello %s' % name


def dec_function_arg(*args):
    return args


def dec_function_error():
    raise RuntimeError('Error for test')


class TestDecorated(unittest.TestCase):
    """Test the decorated function"""

    def test_decorated_output(self):
        # GIVEN
        wrapping_mock = mock.Mock(spec=DecWrapper)

        # WHEN
        output = decorated(wrapping=wrapping_mock, func=dec_function)

        # THEN
        self.assertIsNotNone(output, msg='Output should not be none')
        self.assertEqual(output.__name__, 'dec_function', msg='Returned function should have the same name')

    def test_decorated_without_argument_injection(self):
        # GIVEN
        wrapping_mock = mock.Mock(spec=DecWrapper)
        wrapping_mock.inject_arg = False

        # WHEN
        output = decorated(wrapping=wrapping_mock, func=dec_function)('World')

        # THEN
        self.assertEqual(output, 'Hello World', 'Function output should not change')
        wrapping_mock.start.assert_called_once_with()
        wrapping_mock.shutdown.assert_called_once_with()

    def test_decorated_with_argument_injection(self):
        # GIVEN
        wrapping_mock = mock.Mock(spec=DecWrapper)
        wrapping_mock.inject_arg = True
        wrapping_mock.get_args.return_value = ['First arg']

        # WHEN
        output = decorated(wrapping=wrapping_mock, func=dec_function_arg)('Hello World')

        # THEN
        self.assertIsInstance(output, tuple, 'Should retrieve function arguments')
        self.assertEqual(output[0], 'Hello World', 'Function second output should be the argument parameter')
        self.assertEqual(output[1], 'First arg', 'Function first output should be the wrapping args')
        wrapping_mock.start.assert_called_once_with()
        wrapping_mock.shutdown.assert_called_once_with()

    def test_decorated_exception_raised(self):
        # GIVEN
        wrapping_mock = mock.Mock(spec=DecWrapper)
        wrapping_mock.inject_arg = False

        # WHEN
        f = decorated(wrapping=wrapping_mock, func=dec_function_error)
        with self.assertRaises(RuntimeError) as cm:
            f()

        # THEN
        self.assertEqual(
            str(cm.exception),
            'Error for test',
            'A error should be raised'
        )
        wrapping_mock.start.assert_called_once_with()
        wrapping_mock.shutdown.assert_called_once_with()


if __name__ == '__main__':
    unittest.main()
