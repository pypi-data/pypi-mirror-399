"""
@file    : __init__.py
@author  : yingHan/嬴寒
@email   : yinghan22@163.com
@create  : 2025/12/5 14:50
"""

import inspect
from enum import Enum
from typing import Callable, Any, Optional, Union

from sanic.views import HTTPMethodView


class RequestMethod(Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    OPTIONS = "OPTIONS"
    HEAD = "HEAD"
    PATCH = "PATCH"
    TRACE = "TRACE"


__viewFlag__ = "__isView__"
__viewName__ = "__viewRouter__"


def __isFunction__(target: Any) -> bool:
    return inspect.isfunction(target)


def RequestMapping(
        uri: str,
        requestMethods: list[RequestMethod] | RequestMethod | None = None,
        host: Optional[Union[str, list[str]]] = None,
        strict_slashes: Optional[bool] = None,
        stream: bool = False,
        version: Optional[Union[int, str, float]] = None,
        name: Optional[str] = None,
        ignore_body: bool = False,
        apply: bool = True,
        subprotocols: Optional[list[str]] = None,
        websocket: bool = False,
        unquote: bool = False,
        static: bool = False,
        version_prefix: str = "/v",
        error_format: Optional[str] = None,
        **ctx_kwargs: Any,
):
    def decorator(target, *args, **kwargs) -> Any:
        setattr(target, __viewFlag__, True)
        attr = {"uri": uri, "handler": target, "stream": stream, 'host': host, 'strict_slashes': strict_slashes, 'version': version,
                'name': name, 'ignore_body': ignore_body, 'apply': apply, 'subprotocols': subprotocols, 'websocket': websocket,
                'unquote': unquote, 'static': static, 'version_prefix': version_prefix, 'error_format': error_format,
                **ctx_kwargs}
        if inspect.isclass(target):
            if not issubclass(target, HTTPMethodView):
                new_cls = type(
                    target.__name__,  # 保持类名不变
                    (HTTPMethodView, target),  # 关键：多重继承，先继承 BaseNode
                    dict(target.__dict__),  # 复制原始类的所有属性和方法
                )

                # 保持新类的文档字符串和模块信息
                new_cls.__doc__ = target.__doc__
                new_cls.__module__ = target.__module__
                target = new_cls
            attr["handler"] = getattr(target, "as_view")()
        elif inspect.isfunction(target) and requestMethods is not None:
            attr["methods"] = (
                (
                    [item.value for item in requestMethods]
                    if type(requestMethods) is list
                    else [RequestMethod(requestMethods).value]
                )
                if requestMethods is not None
                else None
            )

        setattr(target, __viewName__, attr)
        return target

    return decorator


def GetMapping(
        uri: str,
        host: Optional[Union[str, list[str]]] = None,
        strict_slashes: Optional[bool] = None,
        version: Optional[Union[int, str, float]] = None,
        name: Optional[str] = None,
        ignore_body: bool = True,
        version_prefix: str = "/v",
        error_format: Optional[str] = None,
        **ctx_kwargs: Any,
):
    return RequestMapping(
        uri,
        RequestMethod.GET,
        host=host,
        strict_slashes=strict_slashes,
        version=version,
        name=name,
        ignore_body=ignore_body,
        version_prefix=version_prefix,
        error_format=error_format,
        **ctx_kwargs,
    )


def PutMapping(
        uri: str,
        host: Optional[Union[str, list[str]]] = None,
        strict_slashes: Optional[bool] = None,
        version: Optional[Union[int, str, float]] = None,
        name: Optional[str] = None,
        ignore_body: bool = True,
        version_prefix: str = "/v",
        error_format: Optional[str] = None,
        **ctx_kwargs: Any,
) -> Callable[[Callable[[Any], Any]], Any]:
    return RequestMapping(
        uri,
        RequestMethod.PUT,
        host=host,
        strict_slashes=strict_slashes,
        version=version,
        name=name,
        ignore_body=ignore_body,
        version_prefix=version_prefix,
        error_format=error_format,
        **ctx_kwargs,
    )


def PostMapping(
        uri: str,
        host: Optional[Union[str, list[str]]] = None,
        strict_slashes: Optional[bool] = None,
        version: Optional[Union[int, str, float]] = None,
        name: Optional[str] = None,
        ignore_body: bool = True,
        version_prefix: str = "/v",
        error_format: Optional[str] = None,
        **ctx_kwargs: Any,
) -> Callable[[Callable[[Any], Any]], Any]:
    return RequestMapping(
        uri,
        RequestMethod.POST,
        host=host,
        strict_slashes=strict_slashes,
        version=version,
        name=name,
        ignore_body=ignore_body,
        version_prefix=version_prefix,
        error_format=error_format,
        **ctx_kwargs,
    )


def DeleteMapping(
        uri: str,
        host: Optional[Union[str, list[str]]] = None,
        strict_slashes: Optional[bool] = None,
        version: Optional[Union[int, str, float]] = None,
        name: Optional[str] = None,
        ignore_body: bool = True,
        version_prefix: str = "/v",
        error_format: Optional[str] = None,
        **ctx_kwargs: Any,
) -> Callable[[Callable[[Any], Any]], Any]:
    return RequestMapping(
        uri,
        RequestMethod.DELETE,
        host=host,
        strict_slashes=strict_slashes,
        version=version,
        name=name,
        ignore_body=ignore_body,
        version_prefix=version_prefix,
        error_format=error_format,
        **ctx_kwargs,
    )


def HeadMapping(
        uri: str,
        host: Optional[Union[str, list[str]]] = None,
        strict_slashes: Optional[bool] = None,
        version: Optional[Union[int, str, float]] = None,
        name: Optional[str] = None,
        ignore_body: bool = True,
        version_prefix: str = "/v",
        error_format: Optional[str] = None,
        **ctx_kwargs: Any,
) -> Callable[[Callable[[Any], Any]], Any]:
    return RequestMapping(
        uri,
        RequestMethod.HEAD,
        host=host,
        strict_slashes=strict_slashes,
        version=version,
        name=name,
        ignore_body=ignore_body,
        version_prefix=version_prefix,
        error_format=error_format,
        **ctx_kwargs,
    )


def WebSocket(uri: str):
    return RequestMapping(uri, requestMethods=None, websocket=True)


def Websocket(uri: str):
    return RequestMapping(uri, requestMethods=None, websocket=True)


def websocket(uri: str):
    return RequestMapping(uri, requestMethods=None, websocket=True)
