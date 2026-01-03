"""
@file    : Controller.py
@author  : yingHan/嬴寒
@email   : yinghan22@163.com
@create  : 2025/12/3 16:12
"""

import inspect
from types import FunctionType
from typing import Any, Callable


def Task(*args, **kwargs) -> Callable[..., Any]:
    if callable(args[0]):
        handler = args[0]
        setattr(handler, "__isTask__", True)
        setattr(handler, "__task__", {"name": None})
        return handler
    else:
        handler: FunctionType
        name: str
        if len(args) == 1:
            if inspect.isfunction(object=args[0]):
                handler = args[0]
            elif type(args[0]) is str:
                name = args[0]
        if "name" in kwargs:
            name = kwargs["name"]
        if "taskName" in kwargs:
            name = kwargs["taskName"]

        def __decorator__(*dArgs, **dKwargs) -> FunctionType:
            nonlocal handler, name

            if len(dArgs) == 1:
                if inspect.isfunction(object=dArgs[0]):
                    handler = dArgs[0]
            if name == "":
                name = handler.__name__

            setattr(handler, "__isTask__", True)
            setattr(handler, "__task__", {"name": name})
            return handler

        return __decorator__
