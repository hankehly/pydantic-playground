import functools
import inspect
import unittest
from typing import Any, List, Optional

from pydantic import ValidationError, create_model


def argtypecheck(fn):
    """
    A decorator that type-checks function arguments

    Raises
    ------
    ValidationError
        If arguments passed to `fn` do not pass type validation


    Examples
    --------
    Examples should be written in doctest format, and should illustrate how
    to use the function.

    >>> @argtypecheck
    >>> def f(x: int, y: str, z = None):
    >>>     pass
    >>>
    >>> f(x="hello world", y=[1, 2, 3])
    pydantic.error_wrappers.ValidationError: 2 validation errors for Args
    x
      value is not a valid integer (type=type_error.integer)
    y
      str type expected (type=type_error.str)

    """

    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        signature = inspect.signature(fn)

        fields = {}
        for param in signature.parameters.values():
            # when no type annotation use the `Any` type to allow any value
            # and if the default value is `None` wrap the annotation in `Optional`
            type_base = Any if param.annotation is param.empty else param.annotation
            type_ = Optional[type_base] if param.default is None else type_base

            # when no default value we mark the argument as required with ( ... )
            # otherwise we use the specified value
            default = ... if param.default is param.empty else param.default

            # specify fields as tuples of the form (<type>, <default value>)
            fields[param.name] = (type_, default)

        # create an instance of BoundArguments to get a clean
        # list of arguments and their assigned values
        arguments = signature.bind(*args, **kwargs).arguments

        # create a dynamic model and validate the arguments
        # by instantiating it
        create_model("Args", **fields)(**arguments)

        return fn(*args, **kwargs)

    return wrapper


class Test(unittest.TestCase):
    """
    Test cases for @argtypecheck decorator
    """

    def test__single(self):
        """
        Simple single argument test case checking most basic behavior
        """

        @argtypecheck
        def f(x: int):
            pass

        with self.assertRaises(ValidationError):
            f("not an integer")

    def test__multiple(self):
        """
        @argtypecheck should handle any number of arguments
        """

        @argtypecheck
        def f(x: int, y: List[str]):
            pass

        try:
            f(("not", "an", "integer"), [{"not": "a list of strings"}])
        except ValidationError as e:
            errors = e.errors()
            self.assertEqual(len(errors), 2)

            # For a definition of the errors list schema see
            # https://pydantic-docs.helpmanual.io/usage/models/#error-handling
            field_1 = errors[0]["loc"][0]
            field_2 = errors[1]["loc"][0]

            self.assertEqual(field_1, "x")
            self.assertEqual(field_2, "y")

    def test__defaults(self):
        """
        @argtypecheck should not throw errors for optional arguments
        """

        @argtypecheck
        def f(x: int, y=None):
            return True

        self.assertTrue(f(123))

    def test__instancemethod(self):
        """
        @argtypecheck should handle type checks for instance methods too
        """

        class _Test:
            @argtypecheck
            def f(self, x: int):
                return True

        t = _Test()

        self.assertTrue(t.f(123))

        with self.assertRaises(ValidationError):
            t.f(x="not a number")

    def test__classmethod(self):
        """
        @argtypecheck should handle type checks for class methods
        """

        class _Test:
            @classmethod
            @argtypecheck
            def f(cls, x: int):
                return True

        self.assertTrue(_Test.f(x=123))

        with self.assertRaises(ValidationError):
            _Test.f(x="not a number")

    def test__staticmethod(self):
        """
        @argtypecheck should type check static methods
        """

        class _Test:
            @staticmethod
            @argtypecheck
            def f(x: int):
                return True

        self.assertTrue(_Test.f(x=123))
        self.assertTrue(_Test().f(x=123))

        with self.assertRaises(ValidationError):
            _Test.f(x="not a number")

        with self.assertRaises(ValidationError):
            _Test().f(x="not a number")


if __name__ == "__main__":
    unittest.main()
