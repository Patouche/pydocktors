# -*- coding: utf-8 -*-
import unittest

from docktors.core import DecWrapper, DwArg


class TestDecWrapper(unittest.TestCase):
    def test__check_inputs_prop_undefined(self):
        # GIVEN
        props = {'int_prop': DwArg(argtype=[int], default=1)}
        inputs = {'undefined_prop': 'toto'}

        # WHEN
        with self.assertRaises(SyntaxError) as cm:
            DecWrapper('Test', inputs, props)

        # THEN
        self.assertEqual(cm.exception.message, "[Test] : Option 'undefined_prop' doesn't not exist.")

    def test__check_inputs_bad_int_type(self):
        # GIVEN
        props = {'int_prop': DwArg(argtype=int, default=1)}
        inputs = {'int_prop': 'toto'}

        # WHEN
        with self.assertRaises(TypeError) as cm:
            DecWrapper('Test', inputs, props)

        # THEN
        self.assertEqual(cm.exception.message, "[Test] : Option 'int_prop' bad type. Expected 'int'. Got 'str' instead.")

    def test__check_inputs_ok_int_type(self):
        # GIVEN
        props = {'int_prop': DwArg(argtype=int, default=1)}
        inputs = {'int_prop': 5}

        # WHEN
        wrapper = DecWrapper('Test', inputs, props)

        # THEN
        self.assertEqual(wrapper.p('int_prop'), 5)

    def test__check_inputs_ok_int_type_alternative(self):
        # GIVEN
        props = {'int_prop': DwArg(argtype=int, default=1, alternatives=[(str, lambda (i): int(i))])}
        inputs = {'int_prop': '5'}

        # WHEN
        wrapper = DecWrapper('test', inputs, props)

        # THEN
        self.assertEqual(wrapper.p('int_prop'), 5)

    def test__check_inputs_ok_tuple_list_type(self):
        # GIVEN
        props = {'tuple_list_prop': DwArg(argtype=[(int, str)], default=list())}
        inputs = {'tuple_list_prop': [(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')]}

        # WHEN
        wrapper = DecWrapper('Test', inputs, props)

        # THEN
        self.assertEqual(wrapper.p('tuple_list_prop'), [(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')])

    def test__check_inputs_bad_dict_using_alternative(self):
        # GIVEN
        props = {
            'dict_prop': DwArg(argtype=dict, alternatives=[([(int, int)], lambda (x): x)], default=dict())
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
            cm.exception.message,
            "[Test] : Option 'dict_prop' bad type. Expected 'dict'. Got 'list' instead."
        )

    def test__check_inputs_ok_dict_using_alternative(self):
        # GIVEN
        props = {
            'dict_prop': DwArg(
                argtype=dict,
                alternatives=[
                    ([(int, int)], lambda (v): dict(i for i in v))
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
        props = {'int_prop': DwArg(argtype=[int], default=1)}
        inputs = {}

        # WHEN
        wrapper = DecWrapper('Test', inputs, props)

        # THEN
        self.assertEqual(wrapper.p('int_prop'), 1)


if __name__ == '__main__':
    unittest.main()
