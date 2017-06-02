# -*- coding: utf-8 -*-
import docker
import logging

logger = logging.getLogger(__name__)


class DwArg(object):
    """
    Decorator wrapper arguments.
    """

    def __init__(self, argtype=None, mandatory=False, default=None, alternatives=list()):
        self.argtype = argtype
        self.mandatory = mandatory
        self.default = default
        self.alternatives = alternatives


class DecWrapper(object):
    """
    Decorator wrapper class for parsing inputs args of any type of decorator.
    """

    _global_props = {
        'inject_arg': DwArg(argtype=bool, default=False),
    }

    def __init__(self, name, inputs, props):
        self._inputs = self._check_inputs(name, inputs, props)
        self.inject_arg = self.p('inject_arg')

    @staticmethod
    def _is_type(value, value_type):
        if isinstance(value_type, type):
            return isinstance(value, value_type)

        if isinstance(value_type, list) and isinstance(value, list):
            if len(value_type) != 1:
                raise SyntaxError('Cannot list containing multiple type')
            return all(DecWrapper._is_type(item, value_type[0]) for item in value)

        if isinstance(value_type, tuple) and len(value) == len(value_type):
            return all(DecWrapper._is_type(value[i], value_type[i]) for i in range(len(value)))

        return False

    def _check_inputs(self, name, inputs, wrapper_props):
        """
        Test input arguments
        """
        props = dict(self._global_props)
        props.update(wrapper_props)
        target_inputs = dict()

        for key, val in inputs.iteritems():
            if key not in props:
                raise SyntaxError('%s : Option \'%s\' doesn\'t not exist.' % (name, key))
            prop = props[key]

            alt_func = next((alt[1] for alt in prop.alternatives if DecWrapper._is_type(val, alt[0])), None)
            val = alt_func(val) if alt_func else val

            argtype = prop.argtype
            if not DecWrapper._is_type(val, argtype):
                raise TypeError(
                    '%s : Option \'%s\' bad type. Expected \'%s\'. Got \'%s\' instead.' %
                    (name, key, argtype.__name__, type(val).__name__)
                )

            target_inputs[key] = val

        all_defaults = [(key, val.default) for key, val in props.iteritems() if val.default is not None]
        other_defaults = [(key, val) for key, val in all_defaults if key not in target_inputs]
        target_inputs.update(other_defaults)

        logger.debug('Input args : %s', target_inputs)
        return target_inputs

    def param(self, item):
        return self._inputs.get(item)

    def p(self, item):
        return self.param(item)
