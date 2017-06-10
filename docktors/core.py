# -*- coding: utf-8 -*-
import logging

import functools

logger = logging.getLogger(__name__)


def decorated(wrapping, func):
    """
    Decorate a function with a wrapping class.

    :param wrapping: the wrapping class use to decorate the function
    :param func: the function to decorate
    :return: the decorated function
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        w_name, f_name = wrapping.__class__.__name__, func.__name__
        logger.debug('[%s] Starting before \'%s\' function', w_name, f_name)
        wrapping.start()
        try:
            logger.debug('[%s] Executing \'%s\' function', w_name, f_name)
            func_args = tuple(wrapping.get_args()) + args if wrapping.inject_arg else args
            return func(*func_args, **kwargs)
        except Exception as e:
            logger.error('[%s] Error in \'%s\' function : %s', w_name, f_name, str(e))
            raise e
        finally:
            logger.debug('[%s] Shutdown after \'%s\' function', w_name, f_name)
            wrapping.shutdown()

    return wrapper


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
    def _is_type(name, value, value_type):
        if isinstance(value_type, type):
            return isinstance(value, value_type)

        if isinstance(value_type, list) and isinstance(value, list):
            if len(value_type) != 1:
                raise SyntaxError('[{name}] Cannot list containing multiple type'.format(name=name))
            return all(DecWrapper._is_type(name, item, value_type[0]) for item in value)

        if isinstance(value_type, tuple) and len(value) == len(value_type):
            return all(DecWrapper._is_type(name, value[i], value_type[i]) for i in range(len(value)))

        return False

    def start(self):
        raise NotImplementedError("Abstract method should be implemented")

    def get_args(self):
        raise NotImplementedError("Abstract method should be implemented")

    def shutdown(self):
        raise NotImplementedError("Abstract method should be implemented")

    def _check_inputs(self, name, inputs, wrapper_props):
        """
        Test input arguments
        """
        props = dict(self._global_props)
        props.update(wrapper_props)
        target_inputs = dict()

        for key, value in inputs.items():
            if key not in props:
                raise SyntaxError("[{name}] : Option '{key}' doesn't not exist.".format(name=name, key=key))
            prop = props[key]

            alt_func = next((alt[1] for alt in prop.alternatives if DecWrapper._is_type(name, value, alt[0])), None)
            target_value = alt_func(value) if alt_func else value

            argtype = prop.argtype
            if not DecWrapper._is_type(name, target_value, argtype):
                raise TypeError("[{name}] : Option '{key}' bad type. Expected '{arg}'. Got '{got}' instead.".format(
                    name=name,
                    key=key,
                    arg=argtype.__name__,
                    got=type(target_value).__name__
                ))

            target_inputs[key] = target_value

        all_defaults = [(key, value.default) for key, value in props.items() if value.default is not None]
        other_defaults = [(key, value) for key, value in all_defaults if key not in target_inputs]
        target_inputs.update(other_defaults)

        logger.debug('[%s] Input args : %s', name, target_inputs)
        return target_inputs

    def param(self, item):
        return self._inputs.get(item)

    def p(self, item):
        return self.param(item)
