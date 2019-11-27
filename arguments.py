import functools
import inspect
from typing import Any, Dict, Optional

from pydantic import create_model, ValidationError


def typecheck(fn):
    def gettype(param: inspect.Parameter):
        if param.annotation is param.empty and param.default is None:
            return Optional[Any]
        elif param.annotation is param.empty:
            return Any
        else:
            return param.annotation

    def getdefault(param: inspect.Parameter):
        return param.empty if param.default is param.empty else param.default

    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        signature = inspect.signature(fn)

        fields = {}
        for param in signature.parameters.values():
            fields[param.name] = (gettype(param), getdefault(param))

        arguments = signature.bind(*args, **kwargs).arguments
        model = create_model("Args", **fields)

        try:
            print(f"fields: {fields}")
            print(f"arguments: {arguments}")
            m = model(**arguments)
            print(f"schema: {m.schema()}")
        except ValidationError as e:
            print(e)

            return

        return fn(*args, **kwargs)

    return wrapper


@typecheck
def f(x: int, y: str, z: float = None):
    print(f"valid(x={x}, y={y}, z={z})")


f(x="not a number", y="hello", z=6)
