# -*- coding: utf-8 -*-
"""
Core module to define :

* The decorated method for created new decorator
* The generic wrapper with input parameters validation.
"""
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
        """Wrapper for decorated function."""
        w_name, f_name = wrapping.__class__.__name__, func.__name__
        logger.debug('[%s] Starting before \'%s\' function', w_name, f_name)
        wrapping.start()
        try:
            logger.debug('[%s] Executing \'%s\' function', w_name, f_name)
            func_args = tuple(wrapping.get_args()) + args if wrapping.inject_arg else args
            return func(*func_args, **kwargs)
        except Exception as ex:
            logger.error('[%s] Error in \'%s\' function : %s', w_name, f_name, str(ex))
            raise ex
        finally:
            logger.debug('[%s] Shutdown after \'%s\' function', w_name, f_name)
            wrapping.shutdown()

    return wrapper


class DecWrapper(object):
    """
    Decorator wrapper class for parsing inputs args of any type of decorator.
    """

    _global_props = dict(
        inject_arg=dict(argtype=bool, default=False),
    )

    def __init__(self, name, inputs, props):
        self._inputs = self.__check_inputs(name, inputs, props)
        self.inject_arg = self.p('inject_arg')

    @staticmethod
    def __is_type(name, value, value_type):
        if isinstance(value_type, type):
            return isinstance(value, value_type)

        if isinstance(value_type, list) and isinstance(value, list):
            if len(value_type) != 1:
                raise SyntaxError('[{name}] Cannot list containing multiple type'.format(name=name))
            return all(DecWrapper.__is_type(name, item, value_type[0]) for item in value)

        if isinstance(value_type, tuple) and len(value) == len(value_type):
            return all(DecWrapper.__is_type(name, value[i], value_type[i]) for i in range(len(value)))

        return False

    def start(self):
        """
        Start method.

        This method will be executed before the decorated function.
        """
        raise NotImplementedError("Abstract method should be implemented")

    def get_args(self):
        """
        When input args is specified, return the inputs args to add for the decorated function.

        This method will be executed after the decorated function returns.
        :return the arguments to include into the decorated function as a list.
        """
        raise NotImplementedError("Abstract method should be implemented")

    def shutdown(self):
        """
        Shutdown method.

        This method will be executed after the decorated function returns.
        """
        raise NotImplementedError("Abstract method should be implemented")

    def __check_inputs(self, name, inputs, wrapper_props):
        """ Test input arguments """
        props = dict(self._global_props)
        props.update(wrapper_props)

        for prop_name, prop_def in props.items():
            if prop_def.get('mandatory', False) and prop_name not in inputs:
                raise SyntaxError("[{name}] : Mandatory option '{key}' is missing.".format(name=name, key=prop_name))

        target_inputs = DecWrapper.__check_user_inputs(name, inputs, props)

        logger.debug('[%s] Input args : %s', name, target_inputs)
        return target_inputs

    @staticmethod
    def __check_user_inputs(name, inputs, props):
        """Check user inputs"""

        default_inputs = [(k, v.get('default')) for k, v in props.items() if v.get('default') is not None]

        target_inputs = dict(default_inputs)

        for key, value in inputs.items():
            if key not in props:
                raise SyntaxError("[{name}] : Option '{key}' doesn't not exist.".format(name=name, key=key))
            prop = props[key]

            # Check for alternative definition of parameters
            alternatives = prop.get('alternatives', [])
            alt_func = next((alt[1] for alt in alternatives if DecWrapper.__is_type(name, value, alt[0])), None)
            target_value = alt_func(value) if alt_func else value

            argtype = prop['argtype']
            if not DecWrapper.__is_type(name, target_value, argtype):
                raise TypeError("[{name}] : Option '{key}' bad type. Expected '{arg}'. Got '{got}' instead.".format(
                    name=name,
                    key=key,
                    arg=argtype.__name__,
                    got=type(target_value).__name__
                ))

            target_inputs[key] = target_value

        return target_inputs

    def param(self, item):
        """
        Retrieve the input parameters.

        :param item: the name of the param to retrieve
        :return: the parameters value
        """
        return self._inputs.get(item)

    def p(self, item):  # pylint: disable=locally-disabled, invalid-name
        """
        Alias for param() method.

        :param item: the name of the param to retrieve
        :return: the parameters value
        """
        return self.param(item)
