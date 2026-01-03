from sanic import HTTPResponse, Request, text
from sanic_boot.core import GetMapping


@GetMapping("/test")
async def test(request: Request) -> HTTPResponse:
    return text("hello")
