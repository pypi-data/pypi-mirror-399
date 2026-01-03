"""
@file    : Controller.py
@author  : yingHan/嬴寒
@email   : yinghan22@163.com
@create  : 2025/12/3 16:12
"""

import re


def __insert_space__(text):
    return re.sub(r"(?<!^)(?=[A-Z])", " ", text)


def __to_kebab_case__(text):
    return __insert_space__(text).lower().replace(" ", "-")


def Controller(*args, **kwargs):  # -> Callable[..., Any]:
    """
    Controller 控制器注册

    :param kwargs['uri'] {str} 命名参数，指定 Controller 的路由路径
    """
    if (len(args) == 1 and type(args[0]) is str) or "uri" in kwargs:
        url: str = ""
        if len(args) == 1:
            uri = args[0]
        if "uri" in kwargs:
            uri = kwargs.get("uri")

        def decoratorWithUri(cls):
            nonlocal uri
            setattr(cls, "__controller__", uri)
            return cls

        return decoratorWithUri
    # else:
    elif callable(args[0]):
        cls = args[0]
        uri = str(cls.__name__.replace("Controller", ""))
        uri = __to_kebab_case__(uri)
        setattr(cls, "__controller__", uri)
        return cls

    def decoratorNoting(cls):
        return cls

    return decoratorNoting
